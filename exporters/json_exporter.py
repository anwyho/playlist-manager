import json
from typing import List, Dict, Any
from datetime import datetime
from services.base import PlaylistExporter
from models import Playlist, Track, Artist, Album


class JSONExporter(PlaylistExporter):
    """Export playlists to JSON format"""
    
    @property
    def file_extension(self) -> str:
        return "json"
    
    @property
    def format_name(self) -> str:
        return "JSON"
    
    def export_playlist(self, playlist: Playlist, file_path: str) -> None:
        """Export a single playlist to JSON"""
        playlist_data = self._serialize_playlist(playlist)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(playlist_data, f, indent=2, ensure_ascii=False, default=str)
    
    def export_playlists(self, playlists: List[Playlist], file_path: str) -> None:
        """Export multiple playlists to JSON"""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_playlists": len(playlists),
            "playlists": [self._serialize_playlist(p) for p in playlists]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
    
    def _serialize_playlist(self, playlist: Playlist) -> Dict[str, Any]:
        """Convert playlist to serializable dictionary"""
        return {
            "id": playlist.id,
            "name": playlist.name,
            "description": playlist.description,
            "uri": playlist.uri,
            "type": playlist.playlist_type.value,
            "public": playlist.public,
            "collaborative": playlist.collaborative,
            "owner": {
                "id": playlist.owner.id,
                "display_name": playlist.owner.display_name,
                "uri": playlist.owner.uri,
                "external_urls": playlist.owner.external_urls
            },
            "follower_count": playlist.follower_count,
            "track_count": playlist.track_count,
            "total_duration_ms": playlist.total_duration_ms,
            "unique_artists": playlist.unique_artists,
            "images": playlist.images,
            "external_urls": playlist.external_urls,
            "snapshot_id": playlist.snapshot_id,
            "created_at": playlist.created_at.isoformat() if playlist.created_at else None,
            "modified_at": playlist.modified_at.isoformat() if playlist.modified_at else None,
            "tracks": [self._serialize_track(track) for track in playlist.tracks]
        }
    
    def _serialize_track(self, track: Track) -> Dict[str, Any]:
        """Convert track to serializable dictionary"""
        return {
            "id": track.id,
            "name": track.name,
            "uri": track.uri,
            "type": track.track_type.value,
            "duration_ms": track.duration_ms,
            "explicit": track.explicit,
            "popularity": track.popularity,
            "preview_url": track.preview_url,
            "track_number": track.track_number,
            "disc_number": track.disc_number,
            "isrc": track.isrc,
            "added_at": track.added_at.isoformat() if track.added_at else None,
            "added_by_user_id": track.added_by_user_id,
            "artists": [self._serialize_artist(artist) for artist in track.artists],
            "album": self._serialize_album(track.album),
            "external_urls": track.external_urls
        }
    
    def _serialize_artist(self, artist: Artist) -> Dict[str, Any]:
        """Convert artist to serializable dictionary"""
        return {
            "id": artist.id,
            "name": artist.name,
            "uri": artist.uri,
            "external_urls": artist.external_urls
        }
    
    def _serialize_album(self, album: Album) -> Dict[str, Any]:
        """Convert album to serializable dictionary"""
        return {
            "id": album.id,
            "name": album.name,
            "uri": album.uri,
            "release_date": album.release_date,
            "album_type": album.album_type,
            "artists": [self._serialize_artist(artist) for artist in album.artists],
            "images": album.images,
            "external_urls": album.external_urls
        }