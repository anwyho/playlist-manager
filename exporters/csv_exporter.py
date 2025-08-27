import csv
from typing import List
from services.base import PlaylistExporter
from models import Playlist


class CSVExporter(PlaylistExporter):
    """Export playlists to CSV format"""
    
    @property
    def file_extension(self) -> str:
        return "csv"
    
    @property
    def format_name(self) -> str:
        return "CSV"
    
    def export_playlist(self, playlist: Playlist, file_path: str) -> None:
        """Export a single playlist to CSV"""
        self._write_csv(file_path, [playlist])
    
    def export_playlists(self, playlists: List[Playlist], file_path: str) -> None:
        """Export multiple playlists to CSV"""
        self._write_csv(file_path, playlists)
    
    def _write_csv(self, file_path: str, playlists: List[Playlist]) -> None:
        """Write playlists to CSV file"""
        fieldnames = [
            'playlist_id', 'playlist_name', 'playlist_description', 'playlist_type',
            'playlist_public', 'playlist_collaborative', 'playlist_owner',
            'playlist_follower_count', 'playlist_track_count', 'playlist_duration_ms',
            'track_id', 'track_name', 'track_uri', 'track_duration_ms', 'track_explicit',
            'track_popularity', 'track_number', 'disc_number', 'track_isrc',
            'track_added_at', 'artist_names', 'album_name', 'album_release_date',
            'album_type', 'spotify_playlist_url', 'spotify_track_url'
        ]
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for playlist in playlists:
                for track in playlist.tracks:
                    artist_names = ', '.join([artist.name for artist in track.artists])
                    
                    row = {
                        'playlist_id': playlist.id,
                        'playlist_name': playlist.name,
                        'playlist_description': playlist.description or '',
                        'playlist_type': playlist.playlist_type.value,
                        'playlist_public': playlist.public,
                        'playlist_collaborative': playlist.collaborative,
                        'playlist_owner': playlist.owner.display_name,
                        'playlist_follower_count': playlist.follower_count,
                        'playlist_track_count': playlist.track_count,
                        'playlist_duration_ms': playlist.total_duration_ms,
                        'track_id': track.id,
                        'track_name': track.name,
                        'track_uri': track.uri,
                        'track_duration_ms': track.duration_ms,
                        'track_explicit': track.explicit,
                        'track_popularity': track.popularity,
                        'track_number': track.track_number,
                        'disc_number': track.disc_number,
                        'track_isrc': track.isrc or '',
                        'track_added_at': track.added_at.isoformat() if track.added_at else '',
                        'artist_names': artist_names,
                        'album_name': track.album.name,
                        'album_release_date': track.album.release_date,
                        'album_type': track.album.album_type,
                        'spotify_playlist_url': playlist.external_urls.get('spotify', ''),
                        'spotify_track_url': track.external_urls.get('spotify', '')
                    }
                    
                    writer.writerow(row)