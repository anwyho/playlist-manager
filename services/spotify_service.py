import asyncio
import aiohttp
from typing import List, Optional, Dict, Any
from datetime import datetime
from services.base import MusicService, MusicServiceError, AuthenticationError, RateLimitError
from models import (
    Playlist, UserProfile, Track, Artist, Album, PlaylistOwner,
    PlaylistType, TrackType
)
from config import SpotifyConfig, TokenManager
from oauth_server import SpotifyAuthenticator


class SpotifyService(MusicService):
    """Real Spotify Web API service implementation"""
    
    BASE_URL = "https://api.spotify.com/v1"
    
    def __init__(self):
        self.config = SpotifyConfig()
        self.token_manager = TokenManager()
        self.authenticator = SpotifyAuthenticator(self.config, self.token_manager)
        self._authenticated = False
        self._user_profile: Optional[UserProfile] = None
    
    async def authenticate(self) -> bool:
        """Authenticate with Spotify using OAuth2"""
        if not self.config.is_configured():
            print("❌ Spotify API not configured")
            print("Run setup first:")
            print("  python3 -c \"from config import SpotifyConfig; SpotifyConfig().setup_interactive()\"")
            return False
        
        success = await self.authenticator.authenticate()
        if success:
            self._authenticated = True
            # Load user profile after authentication
            try:
                self._user_profile = await self.get_user_profile()
            except Exception as e:
                print(f"Warning: Could not load user profile: {e}")
        
        return success
    
    async def get_user_profile(self) -> UserProfile:
        """Get the authenticated user's profile"""
        if not self._authenticated:
            raise AuthenticationError("Not authenticated")
        
        data = await self._make_request("GET", "/me")
        
        return UserProfile(
            id=data["id"],
            display_name=data.get("display_name", data["id"]),
            email=data.get("email", ""),
            country=data.get("country", ""),
            follower_count=data.get("followers", {}).get("total", 0),
            uri=data["uri"],
            external_urls=data.get("external_urls", {}),
            images=data.get("images", []),
            product=data.get("product", "free")
        )
    
    async def get_user_playlists(self, limit: Optional[int] = None) -> List[Playlist]:
        """Get all playlists for the authenticated user"""
        if not self._authenticated:
            raise AuthenticationError("Not authenticated")
        
        playlists = []
        offset = 0
        batch_limit = min(50, limit) if limit else 50  # Spotify max is 50
        
        while True:
            params = {
                "limit": batch_limit,
                "offset": offset
            }
            
            data = await self._make_request("GET", "/me/playlists", params=params)
            
            batch_playlists = [self._parse_playlist_summary(item) for item in data["items"]]
            playlists.extend(batch_playlists)
            
            # Check if we should stop
            if not data.get("next") or (limit and len(playlists) >= limit):
                break
            
            offset += batch_limit
        
        # Limit results if requested
        if limit:
            playlists = playlists[:limit]
        
        # Load detailed track information for each playlist
        for playlist in playlists:
            try:
                detailed_playlist = await self.get_playlist_details(playlist.id)
                playlist.tracks = detailed_playlist.tracks
            except Exception as e:
                print(f"Warning: Could not load tracks for playlist {playlist.name}: {e}")
                playlist.tracks = []
        
        return playlists
    
    async def get_playlist_details(self, playlist_id: str) -> Playlist:
        """Get detailed information about a specific playlist"""
        if not self._authenticated:
            raise AuthenticationError("Not authenticated")
        
        # Get playlist metadata
        playlist_data = await self._make_request("GET", f"/playlists/{playlist_id}")
        
        # Get all tracks for the playlist
        tracks = await self.get_playlist_tracks(playlist_id)
        
        return self._parse_playlist_detailed(playlist_data, tracks)
    
    async def get_playlist_tracks(self, playlist_id: str) -> List[Track]:
        """Get all tracks from a specific playlist"""
        if not self._authenticated:
            raise AuthenticationError("Not authenticated")
        
        tracks = []
        offset = 0
        limit = 50  # Spotify max
        
        while True:
            params = {
                "limit": limit,
                "offset": offset,
                "fields": "items(track(id,name,uri,duration_ms,explicit,popularity,track_number,disc_number,artists(id,name,uri,external_urls),album(id,name,uri,release_date,album_type,artists(id,name,uri,external_urls),images,external_urls),external_urls,external_ids),added_at,added_by(id)),next"
            }
            
            data = await self._make_request("GET", f"/playlists/{playlist_id}/tracks", params=params)
            
            for item in data["items"]:
                if item["track"] and item["track"]["id"]:  # Skip null tracks and local files
                    track = self._parse_track(item["track"], item.get("added_at"), item.get("added_by"))
                    tracks.append(track)
            
            if not data.get("next"):
                break
            
            offset += limit
        
        return tracks
    
    @property
    def service_name(self) -> str:
        return "Spotify"
    
    @property
    def is_authenticated(self) -> bool:
        return self._authenticated and self.token_manager.is_token_valid()
    
    async def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to Spotify API"""
        access_token = self.authenticator.get_access_token()
        if not access_token:
            raise AuthenticationError("No valid access token")
        
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, params=params, json=json_data, headers=headers) as response:
                
                if response.status == 429:  # Rate limited
                    retry_after = int(response.headers.get("Retry-After", 60))
                    raise RateLimitError(f"Rate limited. Retry after {retry_after} seconds")
                
                if response.status == 401:  # Unauthorized
                    raise AuthenticationError("Access token expired or invalid")
                
                if response.status >= 400:
                    error_text = await response.text()
                    raise MusicServiceError(f"API error {response.status}: {error_text}")
                
                return await response.json()
    
    def _parse_playlist_summary(self, data: Dict[str, Any]) -> Playlist:
        """Parse playlist summary data from API response"""
        owner = PlaylistOwner(
            id=data["owner"]["id"],
            display_name=data["owner"]["display_name"],
            uri=data["owner"]["uri"],
            external_urls=data["owner"].get("external_urls", {})
        )
        
        # Determine playlist type
        current_user_id = self._user_profile.id if self._user_profile else None
        if data["owner"]["id"] == current_user_id:
            playlist_type = PlaylistType.COLLABORATIVE if data.get("collaborative", False) else PlaylistType.OWNED
        else:
            playlist_type = PlaylistType.FOLLOWED
        
        return Playlist(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            uri=data["uri"],
            playlist_type=playlist_type,
            public=data.get("public", False),
            collaborative=data.get("collaborative", False),
            owner=owner,
            follower_count=data.get("followers", {}).get("total", 0),
            track_count=data["tracks"]["total"],
            tracks=[],  # Will be populated later
            images=data.get("images", []),
            external_urls=data.get("external_urls", {}),
            snapshot_id=data["snapshot_id"]
        )
    
    def _parse_playlist_detailed(self, data: Dict[str, Any], tracks: List[Track]) -> Playlist:
        """Parse detailed playlist data from API response"""
        playlist = self._parse_playlist_summary(data)
        playlist.tracks = tracks
        return playlist
    
    def _parse_track(self, data: Dict[str, Any], added_at_str: Optional[str] = None, added_by: Optional[Dict] = None) -> Track:
        """Parse track data from API response"""
        # Parse artists
        artists = [
            Artist(
                id=artist["id"],
                name=artist["name"],
                uri=artist["uri"],
                external_urls=artist.get("external_urls", {})
            )
            for artist in data.get("artists", [])
        ]
        
        # Parse album
        album_data = data.get("album", {})
        album_artists = [
            Artist(
                id=artist["id"],
                name=artist["name"], 
                uri=artist["uri"],
                external_urls=artist.get("external_urls", {})
            )
            for artist in album_data.get("artists", [])
        ]
        
        album = Album(
            id=album_data.get("id", ""),
            name=album_data.get("name", ""),
            uri=album_data.get("uri", ""),
            release_date=album_data.get("release_date", ""),
            album_type=album_data.get("album_type", "album"),
            artists=album_artists,
            images=album_data.get("images", []),
            external_urls=album_data.get("external_urls", {})
        )
        
        # Parse added_at timestamp
        added_at = None
        if added_at_str:
            try:
                added_at = datetime.fromisoformat(added_at_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass
        
        # Get ISRC from external_ids
        isrc = None
        if "external_ids" in data:
            isrc = data["external_ids"].get("isrc")
        
        return Track(
            id=data["id"],
            name=data["name"],
            uri=data["uri"],
            track_type=TrackType.TRACK,  # Assuming all are tracks for now
            duration_ms=data.get("duration_ms", 0),
            explicit=data.get("explicit", False),
            popularity=data.get("popularity", 0),
            preview_url=data.get("preview_url"),
            track_number=data.get("track_number", 1),
            disc_number=data.get("disc_number", 1),
            artists=artists,
            album=album,
            external_urls=data.get("external_urls", {}),
            isrc=isrc,
            added_at=added_at,
            added_by_user_id=added_by.get("id") if added_by else None
        )