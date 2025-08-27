import pytest
from datetime import datetime
from models import (
    Playlist, Track, Artist, Album, PlaylistOwner, UserProfile,
    PlaylistType, TrackType
)


class TestModels:
    """Test suite for data models"""

    def test_artist_creation(self):
        """Test Artist model creation"""
        artist = Artist(
            id="artist123",
            name="Test Artist",
            uri="spotify:artist:artist123",
            external_urls={"spotify": "https://spotify.com/artist/artist123"}
        )
        assert artist.id == "artist123"
        assert artist.name == "Test Artist"
        assert artist.uri == "spotify:artist:artist123"

    def test_album_creation(self):
        """Test Album model creation"""
        artist = Artist(
            id="artist123",
            name="Test Artist", 
            uri="spotify:artist:artist123",
            external_urls={"spotify": "https://spotify.com/artist/artist123"}
        )
        album = Album(
            id="album123",
            name="Test Album",
            uri="spotify:album:album123",
            release_date="2023-01-01",
            album_type="album",
            artists=[artist],
            images=[],
            external_urls={"spotify": "https://spotify.com/album/album123"}
        )
        assert album.id == "album123"
        assert album.name == "Test Album"
        assert len(album.artists) == 1
        assert album.artists[0].name == "Test Artist"

    def test_track_creation(self):
        """Test Track model creation"""
        artist = Artist(
            id="artist123",
            name="Test Artist",
            uri="spotify:artist:artist123", 
            external_urls={"spotify": "https://spotify.com/artist/artist123"}
        )
        album = Album(
            id="album123",
            name="Test Album",
            uri="spotify:album:album123",
            release_date="2023-01-01",
            album_type="album",
            artists=[artist],
            images=[],
            external_urls={"spotify": "https://spotify.com/album/album123"}
        )
        track = Track(
            id="track123",
            name="Test Track",
            uri="spotify:track:track123",
            track_type=TrackType.TRACK,
            duration_ms=180000,
            explicit=False,
            popularity=75,
            preview_url="https://preview.com/track123",
            track_number=1,
            disc_number=1,
            artists=[artist],
            album=album,
            external_urls={"spotify": "https://spotify.com/track/track123"}
        )
        assert track.id == "track123"
        assert track.name == "Test Track"
        assert track.duration_ms == 180000
        assert track.track_type == TrackType.TRACK

    def test_playlist_creation(self):
        """Test Playlist model creation"""
        owner = PlaylistOwner(
            id="user123",
            display_name="Test User",
            uri="spotify:user:user123",
            external_urls={"spotify": "https://spotify.com/user/user123"}
        )
        playlist = Playlist(
            id="playlist123",
            name="Test Playlist",
            description="A test playlist",
            uri="spotify:playlist:playlist123",
            playlist_type=PlaylistType.OWNED,
            public=True,
            collaborative=False,
            owner=owner,
            follower_count=100,
            track_count=5,
            tracks=[],
            images=[],
            external_urls={"spotify": "https://spotify.com/playlist/playlist123"},
            snapshot_id="snapshot123"
        )
        assert playlist.id == "playlist123"
        assert playlist.name == "Test Playlist"
        assert playlist.playlist_type == PlaylistType.OWNED
        assert playlist.owner.display_name == "Test User"

    def test_playlist_total_duration(self):
        """Test playlist total duration calculation"""
        owner = PlaylistOwner(
            id="user123",
            display_name="Test User",
            uri="spotify:user:user123",
            external_urls={"spotify": "https://spotify.com/user/user123"}
        )
        artist = Artist(
            id="artist123",
            name="Test Artist",
            uri="spotify:artist:artist123",
            external_urls={"spotify": "https://spotify.com/artist/artist123"}
        )
        album = Album(
            id="album123",
            name="Test Album",
            uri="spotify:album:album123",
            release_date="2023-01-01",
            album_type="album",
            artists=[artist],
            images=[],
            external_urls={"spotify": "https://spotify.com/album/album123"}
        )
        
        tracks = [
            Track(
                id="track1",
                name="Track 1",
                uri="spotify:track:track1",
                track_type=TrackType.TRACK,
                duration_ms=180000,  # 3 minutes
                explicit=False,
                popularity=75,
                preview_url=None,
                track_number=1,
                disc_number=1,
                artists=[artist],
                album=album,
                external_urls={"spotify": "https://spotify.com/track/track1"}
            ),
            Track(
                id="track2",
                name="Track 2",
                uri="spotify:track:track2",
                track_type=TrackType.TRACK,
                duration_ms=240000,  # 4 minutes
                explicit=False,
                popularity=80,
                preview_url=None,
                track_number=2,
                disc_number=1,
                artists=[artist],
                album=album,
                external_urls={"spotify": "https://spotify.com/track/track2"}
            )
        ]
        
        playlist = Playlist(
            id="playlist123",
            name="Test Playlist",
            description="A test playlist",
            uri="spotify:playlist:playlist123",
            playlist_type=PlaylistType.OWNED,
            public=True,
            collaborative=False,
            owner=owner,
            follower_count=100,
            track_count=2,
            tracks=tracks,
            images=[],
            external_urls={"spotify": "https://spotify.com/playlist/playlist123"},
            snapshot_id="snapshot123"
        )
        
        assert playlist.total_duration_ms == 420000  # 7 minutes

    def test_playlist_unique_artists(self):
        """Test playlist unique artists calculation"""
        owner = PlaylistOwner(
            id="user123",
            display_name="Test User",
            uri="spotify:user:user123",
            external_urls={"spotify": "https://spotify.com/user/user123"}
        )
        
        artist1 = Artist(
            id="artist1",
            name="Artist One",
            uri="spotify:artist:artist1",
            external_urls={"spotify": "https://spotify.com/artist/artist1"}
        )
        artist2 = Artist(
            id="artist2", 
            name="Artist Two",
            uri="spotify:artist:artist2",
            external_urls={"spotify": "https://spotify.com/artist/artist2"}
        )
        
        album = Album(
            id="album123",
            name="Test Album",
            uri="spotify:album:album123",
            release_date="2023-01-01",
            album_type="album",
            artists=[artist1],
            images=[],
            external_urls={"spotify": "https://spotify.com/album/album123"}
        )
        
        tracks = [
            Track(
                id="track1",
                name="Track 1",
                uri="spotify:track:track1",
                track_type=TrackType.TRACK,
                duration_ms=180000,
                explicit=False,
                popularity=75,
                preview_url=None,
                track_number=1,
                disc_number=1,
                artists=[artist1],  # Artist One
                album=album,
                external_urls={"spotify": "https://spotify.com/track/track1"}
            ),
            Track(
                id="track2",
                name="Track 2",
                uri="spotify:track:track2",
                track_type=TrackType.TRACK,
                duration_ms=240000,
                explicit=False,
                popularity=80,
                preview_url=None,
                track_number=2,
                disc_number=1,
                artists=[artist2],  # Artist Two
                album=album,
                external_urls={"spotify": "https://spotify.com/track/track2"}
            ),
            Track(
                id="track3",
                name="Track 3",
                uri="spotify:track:track3",
                track_type=TrackType.TRACK,
                duration_ms=200000,
                explicit=False,
                popularity=70,
                preview_url=None,
                track_number=3,
                disc_number=1,
                artists=[artist1],  # Artist One again
                album=album,
                external_urls={"spotify": "https://spotify.com/track/track3"}
            )
        ]
        
        playlist = Playlist(
            id="playlist123",
            name="Test Playlist",
            description="A test playlist",
            uri="spotify:playlist:playlist123",
            playlist_type=PlaylistType.OWNED,
            public=True,
            collaborative=False,
            owner=owner,
            follower_count=100,
            track_count=3,
            tracks=tracks,
            images=[],
            external_urls={"spotify": "https://spotify.com/playlist/playlist123"},
            snapshot_id="snapshot123"
        )
        
        unique_artists = playlist.unique_artists
        assert len(unique_artists) == 2
        assert "Artist One" in unique_artists
        assert "Artist Two" in unique_artists
        assert unique_artists == ["Artist One", "Artist Two"]  # Should be sorted

    def test_user_profile_creation(self):
        """Test UserProfile model creation"""
        user = UserProfile(
            id="user123",
            display_name="Test User",
            email="test@example.com",
            country="US",
            follower_count=50,
            uri="spotify:user:user123",
            external_urls={"spotify": "https://spotify.com/user/user123"},
            images=[],
            product="premium"
        )
        assert user.id == "user123"
        assert user.display_name == "Test User"
        assert user.email == "test@example.com"
        assert user.product == "premium"