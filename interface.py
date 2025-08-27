import asyncio
from typing import List, Dict, Optional
from services.base import MusicService
from models import Playlist, PlaylistType
from datetime import datetime


class PlaylistSelector:
    """Interactive interface for selecting playlists"""
    
    def __init__(self, music_service: MusicService):
        self.music_service = music_service
        self.playlists: List[Playlist] = []
    
    async def load_playlists(self) -> None:
        """Load all user playlists from the music service"""
        print(f"Loading playlists from {self.music_service.service_name}...")
        self.playlists = await self.music_service.get_user_playlists()
        print(f"Found {len(self.playlists)} playlists")
    
    def display_playlists(self) -> None:
        """Display all playlists in a formatted table"""
        if not self.playlists:
            print("No playlists found.")
            return
        
        print("\n" + "="*100)
        print(f"{'#':<3} {'Name':<30} {'Type':<12} {'Tracks':<8} {'Public':<8} {'Owner':<20}")
        print("="*100)
        
        for i, playlist in enumerate(self.playlists, 1):
            playlist_type = playlist.playlist_type.value
            track_count = len(playlist.tracks)
            public_status = "Yes" if playlist.public else "No"
            owner_name = playlist.owner.display_name[:19]
            
            print(f"{i:<3} {playlist.name[:29]:<30} {playlist_type:<12} {track_count:<8} {public_status:<8} {owner_name:<20}")
        
        print("="*100)
    
    def display_playlist_details(self, playlist_index: int) -> None:
        """Display detailed information about a specific playlist"""
        if playlist_index < 0 or playlist_index >= len(self.playlists):
            print("Invalid playlist index")
            return
        
        playlist = self.playlists[playlist_index]
        
        print(f"\n{'='*80}")
        print(f"Playlist: {playlist.name}")
        print(f"{'='*80}")
        print(f"Description: {playlist.description or 'No description'}")
        print(f"Owner: {playlist.owner.display_name}")
        print(f"Type: {playlist.playlist_type.value}")
        print(f"Public: {'Yes' if playlist.public else 'No'}")
        print(f"Collaborative: {'Yes' if playlist.collaborative else 'No'}")
        print(f"Followers: {playlist.follower_count:,}")
        print(f"Total Tracks: {len(playlist.tracks)}")
        print(f"Total Duration: {self._format_duration(playlist.total_duration_ms)}")
        print(f"Unique Artists: {len(playlist.unique_artists)}")
        
        if playlist.created_at:
            print(f"Created: {playlist.created_at.strftime('%Y-%m-%d')}")
        if playlist.modified_at:
            print(f"Last Modified: {playlist.modified_at.strftime('%Y-%m-%d')}")
        
        print(f"\nTracks:")
        print(f"{'#':<3} {'Title':<35} {'Artist':<25} {'Duration':<8}")
        print("-" * 80)
        
        for i, track in enumerate(playlist.tracks, 1):
            artist_names = ", ".join([artist.name for artist in track.artists])
            duration = self._format_duration(track.duration_ms)
            
            print(f"{i:<3} {track.name[:34]:<35} {artist_names[:24]:<25} {duration:<8}")
        
        print(f"{'='*80}")
    
    def select_playlists_interactive(self) -> List[Playlist]:
        """Interactive playlist selection interface"""
        if not self.playlists:
            print("No playlists available for selection.")
            return []
        
        selected_playlists = []
        
        while True:
            print("\n" + "="*50)
            print("PLAYLIST SELECTION MENU")
            print("="*50)
            print("1. View all playlists")
            print("2. View playlist details")
            print("3. Select playlist(s)")
            print("4. Select by type (owned/followed/collaborative)")
            print("5. Select all playlists")
            print("6. View current selection")
            print("7. Clear selection")
            print("8. Done selecting")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-8): ").strip()
            
            if choice == "0":
                return []
            elif choice == "1":
                self.display_playlists()
            elif choice == "2":
                self._handle_playlist_details()
            elif choice == "3":
                selected = self._handle_individual_selection()
                selected_playlists.extend(selected)
            elif choice == "4":
                selected = self._handle_type_selection()
                selected_playlists.extend(selected)
            elif choice == "5":
                selected_playlists = self.playlists.copy()
                print(f"Selected all {len(selected_playlists)} playlists")
            elif choice == "6":
                self._display_selection(selected_playlists)
            elif choice == "7":
                selected_playlists.clear()
                print("Selection cleared")
            elif choice == "8":
                if selected_playlists:
                    return list(set(selected_playlists))  # Remove duplicates
                else:
                    print("No playlists selected.")
            else:
                print("Invalid choice. Please try again.")
    
    def _handle_playlist_details(self) -> None:
        """Handle viewing playlist details"""
        self.display_playlists()
        try:
            index = int(input("Enter playlist number to view details: ")) - 1
            self.display_playlist_details(index)
        except (ValueError, IndexError):
            print("Invalid playlist number")
    
    def _handle_individual_selection(self) -> List[Playlist]:
        """Handle individual playlist selection"""
        self.display_playlists()
        selected = []
        
        input_str = input("Enter playlist numbers (comma-separated, e.g., 1,3,5): ").strip()
        if not input_str:
            return selected
        
        try:
            indices = [int(x.strip()) - 1 for x in input_str.split(",")]
            for index in indices:
                if 0 <= index < len(self.playlists):
                    selected.append(self.playlists[index])
                    print(f"Selected: {self.playlists[index].name}")
                else:
                    print(f"Invalid playlist number: {index + 1}")
        except ValueError:
            print("Invalid input format")
        
        return selected
    
    def _handle_type_selection(self) -> List[Playlist]:
        """Handle selection by playlist type"""
        print("\nPlaylist Types:")
        print("1. Owned playlists")
        print("2. Followed playlists") 
        print("3. Collaborative playlists")
        
        type_choice = input("Select type (1-3): ").strip()
        type_map = {
            "1": PlaylistType.OWNED,
            "2": PlaylistType.FOLLOWED,
            "3": PlaylistType.COLLABORATIVE
        }
        
        if type_choice not in type_map:
            print("Invalid type selection")
            return []
        
        selected_type = type_map[type_choice]
        matching_playlists = [p for p in self.playlists if p.playlist_type == selected_type]
        
        if matching_playlists:
            print(f"Selected {len(matching_playlists)} {selected_type.value} playlists:")
            for playlist in matching_playlists:
                print(f"  - {playlist.name}")
        else:
            print(f"No {selected_type.value} playlists found")
        
        return matching_playlists
    
    def _display_selection(self, selected_playlists: List[Playlist]) -> None:
        """Display currently selected playlists"""
        if not selected_playlists:
            print("No playlists currently selected")
            return
        
        print(f"\nCurrently Selected Playlists ({len(selected_playlists)}):")
        print("-" * 50)
        for i, playlist in enumerate(selected_playlists, 1):
            tracks = len(playlist.tracks)
            duration = self._format_duration(playlist.total_duration_ms)
            print(f"{i}. {playlist.name} ({tracks} tracks, {duration})")
    
    def _format_duration(self, duration_ms: int) -> str:
        """Format duration from milliseconds to human readable format"""
        total_seconds = duration_ms // 1000
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"


async def main():
    """Demo the interface with mock data"""
    from services.mock_spotify import MockSpotifyService
    
    # Initialize mock service
    service = MockSpotifyService()
    await service.authenticate()
    
    # Create and use selector
    selector = PlaylistSelector(service)
    await selector.load_playlists()
    
    # Run interactive selection
    selected = selector.select_playlists_interactive()
    
    if selected:
        print(f"\nFinal selection: {len(selected)} playlists")
        for playlist in selected:
            print(f"  - {playlist.name}")
    else:
        print("\nNo playlists selected.")


if __name__ == "__main__":
    asyncio.run(main())