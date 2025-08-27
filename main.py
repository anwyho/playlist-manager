#!/usr/bin/env python3
import asyncio
import os
from datetime import datetime
from typing import List, Dict
from pathlib import Path

from services.mock_spotify import MockSpotifyService
from services.spotify_service import SpotifyService
from interface import PlaylistSelector
from exporters.json_exporter import JSONExporter
from exporters.csv_exporter import CSVExporter
from services.base import PlaylistExporter
from models import Playlist
from config import SpotifyConfig


class PlaylistManager:
    """Main application for managing playlist backups and exports"""
    
    def __init__(self):
        self.music_service = None
        self.exporters: Dict[str, PlaylistExporter] = {
            'json': JSONExporter(),
            'csv': CSVExporter()
        }
        self.selected_playlists: List[Playlist] = []
    
    async def initialize_service(self, service_type: str = "real") -> bool:
        """Initialize and authenticate with the music service"""
        if service_type == "mock":
            print("🧪 Using mock Spotify service for testing")
            self.music_service = MockSpotifyService()
        elif service_type == "real":
            print("🎵 Using real Spotify service")
            self.music_service = SpotifyService()
        else:
            raise ValueError(f"Unknown service type: {service_type}")
        
        try:
            success = await self.music_service.authenticate()
            if success:
                user_profile = await self.music_service.get_user_profile()
                print(f"Successfully authenticated as: {user_profile.display_name}")
                return True
            else:
                print("Authentication failed")
                return False
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    async def select_playlists(self) -> None:
        """Run the playlist selection interface"""
        if not self.music_service:
            raise Exception("Music service not initialized")
        
        selector = PlaylistSelector(self.music_service)
        await selector.load_playlists()
        
        self.selected_playlists = selector.select_playlists_interactive()
    
    def export_playlists(self, format_type: str, output_dir: str = "exports") -> None:
        """Export selected playlists in the specified format"""
        if not self.selected_playlists:
            print("No playlists selected for export")
            return
        
        if format_type not in self.exporters:
            print(f"Unsupported export format: {format_type}")
            print(f"Available formats: {', '.join(self.exporters.keys())}")
            return
        
        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)
        
        exporter = self.exporters[format_type]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export all playlists to one file
        all_playlists_file = os.path.join(
            output_dir, 
            f"spotify_playlists_{timestamp}.{exporter.file_extension}"
        )
        
        try:
            exporter.export_playlists(self.selected_playlists, all_playlists_file)
            print(f"Exported {len(self.selected_playlists)} playlists to: {all_playlists_file}")
            
            # Also export individual playlist files
            for playlist in self.selected_playlists:
                safe_name = "".join(c for c in playlist.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                individual_file = os.path.join(
                    output_dir,
                    f"{safe_name}_{timestamp}.{exporter.file_extension}"
                )
                
                exporter.export_playlist(playlist, individual_file)
                print(f"  - {playlist.name} → {individual_file}")
                
        except Exception as e:
            print(f"Export error: {e}")
    
    def display_summary(self) -> None:
        """Display summary of selected playlists"""
        if not self.selected_playlists:
            print("No playlists selected")
            return
        
        total_tracks = sum(len(p.tracks) for p in self.selected_playlists)
        total_duration_ms = sum(p.total_duration_ms for p in self.selected_playlists)
        
        # Convert duration to human readable format
        total_seconds = total_duration_ms // 1000
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        print(f"\n{'='*60}")
        print("PLAYLIST BACKUP SUMMARY")
        print(f"{'='*60}")
        print(f"Total Playlists: {len(self.selected_playlists)}")
        print(f"Total Tracks: {total_tracks:,}")
        print(f"Total Duration: {hours:,}h {minutes:02d}m")
        
        # Breakdown by type
        from collections import Counter
        type_counts = Counter(p.playlist_type.value for p in self.selected_playlists)
        print(f"\nBreakdown by Type:")
        for playlist_type, count in type_counts.items():
            print(f"  {playlist_type.title()}: {count}")
        
        print(f"\nPlaylists:")
        for i, playlist in enumerate(self.selected_playlists, 1):
            tracks = len(playlist.tracks)
            duration_mins = playlist.total_duration_ms // 60000
            print(f"  {i:2d}. {playlist.name} ({tracks} tracks, {duration_mins}m)")
        
        print(f"{'='*60}")


async def main():
    """Main application entry point"""
    print("🎵 Spotify Playlist Keeper")
    print("=" * 50)
    
    # Service type selection
    print("Select service type:")
    print("1. Real Spotify API (requires setup)")
    print("2. Mock/Demo service (for testing)")
    
    while True:
        choice = input("Enter choice (1-2): ").strip()
        if choice == "1":
            service_type = "real"
            break
        elif choice == "2":
            service_type = "mock"
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")
    
    manager = PlaylistManager()
    
    # Initialize service
    print(f"Initializing {service_type} service...")
    if not await manager.initialize_service(service_type):
        print("Failed to initialize service. Exiting.")
        return
    
    # Main menu loop
    while True:
        print("\n" + "="*40)
        print("MAIN MENU")
        print("="*40)
        print("1. Select playlists")
        print("2. View current selection")
        print("3. Export to JSON")
        print("4. Export to CSV")
        print("5. View summary")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-5): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            await manager.select_playlists()
        elif choice == "2":
            if manager.selected_playlists:
                print(f"\nSelected Playlists ({len(manager.selected_playlists)}):")
                for i, playlist in enumerate(manager.selected_playlists, 1):
                    print(f"  {i}. {playlist.name}")
            else:
                print("No playlists currently selected")
        elif choice == "3":
            manager.export_playlists("json")
        elif choice == "4":
            manager.export_playlists("csv")
        elif choice == "5":
            manager.display_summary()
        else:
            print("Invalid choice. Please try again.")
    
    print("\nThanks for using Spotify Playlist Keeper! 🎵")


if __name__ == "__main__":
    asyncio.run(main())