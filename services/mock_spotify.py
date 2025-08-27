import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
from services.base import MusicService
from models import (
    Playlist, UserProfile, Track, Artist, Album, PlaylistOwner,
    PlaylistType, TrackType
)


class MockSpotifyService(MusicService):
    """Mock Spotify service for testing and development"""
    
    def __init__(self):
        self._authenticated = False
        self._user_profile = None
        self._playlists = self._generate_mock_playlists()
    
    async def authenticate(self) -> bool:
        await asyncio.sleep(0.1)  # Simulate API call
        self._authenticated = True
        self._user_profile = self._generate_mock_user_profile()
        return True
    
    async def get_user_profile(self) -> UserProfile:
        if not self._authenticated:
            raise Exception("Not authenticated")
        return self._user_profile
    
    async def get_user_playlists(self, limit: Optional[int] = None) -> List[Playlist]:
        if not self._authenticated:
            raise Exception("Not authenticated")
        
        await asyncio.sleep(0.2)  # Simulate API call
        playlists = self._playlists[:limit] if limit else self._playlists
        return playlists
    
    async def get_playlist_details(self, playlist_id: str) -> Playlist:
        if not self._authenticated:
            raise Exception("Not authenticated")
        
        await asyncio.sleep(0.1)
        playlist = next((p for p in self._playlists if p.id == playlist_id), None)
        if not playlist:
            raise Exception(f"Playlist {playlist_id} not found")
        return playlist
    
    async def get_playlist_tracks(self, playlist_id: str) -> List[Track]:
        playlist = await self.get_playlist_details(playlist_id)
        return playlist.tracks
    
    @property
    def service_name(self) -> str:
        return "Spotify"
    
    @property
    def is_authenticated(self) -> bool:
        return self._authenticated
    
    def _generate_mock_user_profile(self) -> UserProfile:
        return UserProfile(
            id="mock_user_123",
            display_name="Test User",
            email="test@example.com",
            country="US",
            follower_count=42,
            uri="spotify:user:mock_user_123",
            external_urls={"spotify": "https://open.spotify.com/user/mock_user_123"},
            images=[{
                "url": "https://i.scdn.co/image/ab67757000003b8255365e307e751b1c2b4cbb9b",
                "height": 300,
                "width": 300
            }],
            product="premium"
        )
    
    def _generate_mock_playlists(self) -> List[Playlist]:
        owner = PlaylistOwner(
            id="mock_user_123",
            display_name="Test User",
            uri="spotify:user:mock_user_123",
            external_urls={"spotify": "https://open.spotify.com/user/mock_user_123"}
        )
        
        # Create mock artists
        taylor_swift = Artist(
            id="06HL4z0CvFAxyc27GXpf02",
            name="Taylor Swift",
            uri="spotify:artist:06HL4z0CvFAxyc27GXpf02",
            external_urls={"spotify": "https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02"}
        )
        
        the_beatles = Artist(
            id="3WrFJ7ztbogyGnTHbHJFl2",
            name="The Beatles",
            uri="spotify:artist:3WrFJ7ztbogyGnTHbHJFl2",
            external_urls={"spotify": "https://open.spotify.com/artist/3WrFJ7ztbogyGnTHbHJFl2"}
        )
        
        radiohead = Artist(
            id="4Z8W4fKeB5YxbusRsdQVPb",
            name="Radiohead",
            uri="spotify:artist:4Z8W4fKeB5YxbusRsdQVPb",
            external_urls={"spotify": "https://open.spotify.com/artist/4Z8W4fKeB5YxbusRsdQVPb"}
        )
        
        # Create mock albums
        folklore = Album(
            id="2fenSS68JI1h4Fo296JfGr",
            name="folklore",
            uri="spotify:album:2fenSS68JI1h4Fo296JfGr",
            release_date="2020-07-24",
            album_type="album",
            artists=[taylor_swift],
            images=[{
                "url": "https://i.scdn.co/image/ab67616d0000b273395427503e0c3535e2ce0c7e",
                "height": 640,
                "width": 640
            }],
            external_urls={"spotify": "https://open.spotify.com/album/2fenSS68JI1h4Fo296JfGr"}
        )
        
        abbey_road = Album(
            id="0ETFjACtuP2ADo6LFhL6HN",
            name="Abbey Road",
            uri="spotify:album:0ETFjACtuP2ADo6LFhL6HN",
            release_date="1969-09-26",
            album_type="album",
            artists=[the_beatles],
            images=[{
                "url": "https://i.scdn.co/image/ab67616d0000b273dc30583ba717007b00cceb25",
                "height": 640,
                "width": 640
            }],
            external_urls={"spotify": "https://open.spotify.com/album/0ETFjACtuP2ADo6LFhL6HN"}
        )
        
        ok_computer = Album(
            id="6dVIqQ8qmQ5GBnJ9shOYGE",
            name="OK Computer",
            uri="spotify:album:6dVIqQ8qmQ5GBnJ9shOYGE",
            release_date="1997-07-01",
            album_type="album",
            artists=[radiohead],
            images=[{
                "url": "https://i.scdn.co/image/ab67616d0000b273c8b444df094279e70d0ed856",
                "height": 640,
                "width": 640
            }],
            external_urls={"spotify": "https://open.spotify.com/album/6dVIqQ8qmQ5GBnJ9shOYGE"}
        )
        
        # Create mock tracks
        cardigan = Track(
            id="4R2kfaDFhslZEMSK0SuBjU",
            name="cardigan",
            uri="spotify:track:4R2kfaDFhslZEMSK0SuBjU",
            track_type=TrackType.TRACK,
            duration_ms=239560,
            explicit=False,
            popularity=85,
            preview_url="https://p.scdn.co/mp3-preview/...",
            track_number=1,
            disc_number=1,
            artists=[taylor_swift],
            album=folklore,
            external_urls={"spotify": "https://open.spotify.com/track/4R2kfaDFhslZEMSK0SuBjU"},
            isrc="USUG22001234",
            added_at=datetime.now() - timedelta(days=30)
        )
        
        come_together = Track(
            id="2EqlS6tkEnglzr7tkKAAYD",
            name="Come Together",
            uri="spotify:track:2EqlS6tkEnglzr7tkKAAYD",
            track_type=TrackType.TRACK,
            duration_ms=259893,
            explicit=False,
            popularity=90,
            preview_url="https://p.scdn.co/mp3-preview/...",
            track_number=1,
            disc_number=1,
            artists=[the_beatles],
            album=abbey_road,
            external_urls={"spotify": "https://open.spotify.com/track/2EqlS6tkEnglzr7tkKAAYD"},
            isrc="GBUMB7700123",
            added_at=datetime.now() - timedelta(days=45)
        )
        
        paranoid_android = Track(
            id="6LgJvl0Xdtc73RJ1WBKQYY",
            name="Paranoid Android",
            uri="spotify:track:6LgJvl0Xdtc73RJ1WBKQYY",
            track_type=TrackType.TRACK,
            duration_ms=383066,
            explicit=False,
            popularity=88,
            preview_url="https://p.scdn.co/mp3-preview/...",
            track_number=2,
            disc_number=1,
            artists=[radiohead],
            album=ok_computer,
            external_urls={"spotify": "https://open.spotify.com/track/6LgJvl0Xdtc73RJ1WBKQYY"},
            isrc="GBAJE9700456",
            added_at=datetime.now() - timedelta(days=60)
        )
        
        playlists = [
            Playlist(
                id="playlist_1",
                name="My Favorite Songs",
                description="A collection of my all-time favorite tracks",
                uri="spotify:playlist:playlist_1",
                playlist_type=PlaylistType.OWNED,
                public=True,
                collaborative=False,
                owner=owner,
                follower_count=23,
                track_count=3,
                tracks=[cardigan, come_together, paranoid_android],
                images=[{
                    "url": "https://mosaic.scdn.co/640/...",
                    "height": 640,
                    "width": 640
                }],
                external_urls={"spotify": "https://open.spotify.com/playlist/playlist_1"},
                snapshot_id="MTY4ODA5NDg4NSwwMDAwMDAwMDAwMDA=",
                created_at=datetime.now() - timedelta(days=90),
                modified_at=datetime.now() - timedelta(days=30)
            ),
            Playlist(
                id="playlist_2", 
                name="Road Trip Vibes",
                description="Perfect songs for long drives",
                uri="spotify:playlist:playlist_2",
                playlist_type=PlaylistType.OWNED,
                public=False,
                collaborative=True,
                owner=owner,
                follower_count=5,
                track_count=2,
                tracks=[come_together, paranoid_android],
                images=[{
                    "url": "https://mosaic.scdn.co/640/...",
                    "height": 640,
                    "width": 640
                }],
                external_urls={"spotify": "https://open.spotify.com/playlist/playlist_2"},
                snapshot_id="MTY4ODA5NDg4NSwwMDAwMDAwMDAwMDE=",
                created_at=datetime.now() - timedelta(days=60),
                modified_at=datetime.now() - timedelta(days=10)
            ),
            Playlist(
                id="playlist_3",
                name="Chill Indie Folk",
                description="Relaxing indie folk for quiet moments",
                uri="spotify:playlist:playlist_3",
                playlist_type=PlaylistType.FOLLOWED,
                public=True,
                collaborative=False,
                owner=PlaylistOwner(
                    id="spotify",
                    display_name="Spotify",
                    uri="spotify:user:spotify",
                    external_urls={"spotify": "https://open.spotify.com/user/spotify"}
                ),
                follower_count=1247,
                track_count=1,
                tracks=[cardigan],
                images=[{
                    "url": "https://i.scdn.co/image/ab67706f00000003...",
                    "height": 640,
                    "width": 640
                }],
                external_urls={"spotify": "https://open.spotify.com/playlist/playlist_3"},
                snapshot_id="MTY4ODA5NDg4NSwwMDAwMDAwMDAwMDI=",
                created_at=datetime.now() - timedelta(days=120)
            )
        ]
        
        return playlists