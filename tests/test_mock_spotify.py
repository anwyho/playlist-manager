import pytest
from datetime import datetime
from unittest.mock import patch
from services.mock_spotify import MockSpotifyService
from models import PlaylistType, TrackType


class TestMockSpotifyService:
    """Test suite for MockSpotifyService"""
    
    @pytest.fixture
    def mock_service(self):
        """Create a MockSpotifyService instance for testing"""
        return MockSpotifyService()
    
    @pytest.mark.asyncio
    async def test_initialization(self, mock_service):
        """Test service initialization"""
        await mock_service.initialize()
        assert mock_service.is_authenticated
        
    @pytest.mark.asyncio
    async def test_get_user_profile(self, mock_service):
        """Test getting user profile"""
        await mock_service.initialize()
        profile = await mock_service.get_user_profile()
        
        assert profile.id == "mock_user_123"
        assert profile.display_name == "Test User"
        assert profile.email == "test@example.com"
        assert profile.country == "US"
        assert profile.product == "premium"
        
    @pytest.mark.asyncio
    async def test_get_playlists(self, mock_service):
        """Test getting user playlists"""
        await mock_service.initialize()
        playlists = await mock_service.get_user_playlists()
        
        assert len(playlists) == 3
        
        # Check first playlist - My Favorite Songs
        favorite_playlist = playlists[0]
        assert favorite_playlist.name == "My Favorite Songs"
        assert favorite_playlist.playlist_type == PlaylistType.OWNED
        assert favorite_playlist.public == True
        assert favorite_playlist.track_count == 3
        assert len(favorite_playlist.tracks) == 3
        
        # Check second playlist - Road Trip Vibes
        road_trip_playlist = playlists[1]
        assert road_trip_playlist.name == "Road Trip Vibes"
        assert road_trip_playlist.playlist_type == PlaylistType.OWNED
        assert road_trip_playlist.public == False
        assert road_trip_playlist.track_count == 2
        
        # Check third playlist - Chill Indie Folk
        indie_playlist = playlists[2]
        assert indie_playlist.name == "Chill Indie Folk"
        assert indie_playlist.playlist_type == PlaylistType.FOLLOWED
        assert indie_playlist.public == True
        assert indie_playlist.track_count == 1
        
    @pytest.mark.asyncio
    async def test_playlist_tracks_structure(self, mock_service):
        """Test playlist tracks have correct structure"""
        await mock_service.initialize()
        playlists = await mock_service.get_user_playlists()
        
        # Test first playlist's tracks
        favorite_playlist = playlists[0]
        tracks = favorite_playlist.tracks
        
        assert len(tracks) == 3
        
        # Check first track
        first_track = tracks[0]
        assert first_track.name == "Bohemian Rhapsody"
        assert first_track.track_type == TrackType.TRACK
        assert first_track.duration_ms == 354000  # 5:54
        assert first_track.explicit == False
        assert first_track.popularity == 95
        assert len(first_track.artists) == 1
        assert first_track.artists[0].name == "Queen"
        assert first_track.album.name == "A Night at the Opera"
        
    @pytest.mark.asyncio 
    async def test_playlist_duration_calculation(self, mock_service):
        """Test playlist total duration calculation"""
        await mock_service.initialize()
        playlists = await mock_service.get_user_playlists()
        
        favorite_playlist = playlists[0]
        expected_duration = 354000 + 253000 + 239000  # Sum of track durations
        assert favorite_playlist.total_duration_ms == expected_duration
        
    @pytest.mark.asyncio
    async def test_playlist_unique_artists(self, mock_service):
        """Test playlist unique artists calculation"""
        await mock_service.initialize()
        playlists = await mock_service.get_user_playlists()
        
        favorite_playlist = playlists[0]
        unique_artists = favorite_playlist.unique_artists
        
        assert len(unique_artists) == 3
        assert "Queen" in unique_artists
        assert "Led Zeppelin" in unique_artists
        assert "The Beatles" in unique_artists
        assert unique_artists == ["Led Zeppelin", "Queen", "The Beatles"]  # Sorted
        
    @pytest.mark.asyncio
    async def test_playlist_owners(self, mock_service):
        """Test playlist owners are correctly set"""
        await mock_service.initialize()
        playlists = await mock_service.get_user_playlists()
        
        # Owned playlists should have "Test User" as owner
        favorite_playlist = playlists[0]
        road_trip_playlist = playlists[1]
        assert favorite_playlist.owner.display_name == "Test User"
        assert road_trip_playlist.owner.display_name == "Test User"
        
        # Followed playlist should have "Spotify" as owner
        indie_playlist = playlists[2]
        assert indie_playlist.owner.display_name == "Spotify"
        
    @pytest.mark.asyncio
    async def test_playlist_metadata(self, mock_service):
        """Test playlist metadata fields"""
        await mock_service.initialize()
        playlists = await mock_service.get_user_playlists()
        
        for playlist in playlists:
            assert playlist.id is not None
            assert playlist.name is not None
            assert playlist.uri is not None
            assert playlist.snapshot_id is not None
            assert playlist.external_urls is not None
            assert "spotify" in playlist.external_urls
            assert playlist.created_at is not None
            assert isinstance(playlist.created_at, datetime)
            
    @pytest.mark.asyncio
    async def test_track_metadata(self, mock_service):
        """Test track metadata fields"""
        await mock_service.initialize()
        playlists = await mock_service.get_user_playlists()
        
        for playlist in playlists:
            for track in playlist.tracks:
                assert track.id is not None
                assert track.name is not None
                assert track.uri is not None
                assert track.duration_ms > 0
                assert track.track_number > 0
                assert track.disc_number > 0
                assert len(track.artists) > 0
                assert track.album is not None
                assert track.external_urls is not None
                
    @pytest.mark.asyncio
    async def test_collaborative_and_public_flags(self, mock_service):
        """Test collaborative and public flags"""
        await mock_service.initialize()
        playlists = await mock_service.get_user_playlists()
        
        # None of the mock playlists should be collaborative
        for playlist in playlists:
            assert playlist.collaborative == False
            
        # Check specific public/private settings
        favorite_playlist = playlists[0]  # My Favorite Songs - public
        road_trip_playlist = playlists[1]  # Road Trip Vibes - private
        indie_playlist = playlists[2]     # Chill Indie Folk - public
        
        assert favorite_playlist.public == True
        assert road_trip_playlist.public == False
        assert indie_playlist.public == True
        
    @pytest.mark.asyncio
    async def test_follower_counts(self, mock_service):
        """Test playlist follower counts"""
        await mock_service.initialize()
        playlists = await mock_service.get_user_playlists()
        
        favorite_playlist = playlists[0]
        road_trip_playlist = playlists[1]
        indie_playlist = playlists[2]
        
        assert favorite_playlist.follower_count == 0  # Own playlist, no followers
        assert road_trip_playlist.follower_count == 5  # Few followers
        assert indie_playlist.follower_count == 1247  # Popular followed playlist
        
    @pytest.mark.asyncio
    async def test_service_without_initialization(self):
        """Test service methods without initialization should fail gracefully"""
        service = MockSpotifyService()
        
        # Should not be authenticated before initialization
        assert not service.is_authenticated
        
        # Methods should handle uninitialized state
        with pytest.raises(Exception):
            await service.get_user_profile()
        with pytest.raises(Exception):
            await service.get_user_playlists()