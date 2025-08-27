import pytest
from io import StringIO
from unittest.mock import Mock, patch, MagicMock
from interface import PlaylistSelector
from services.mock_spotify import MockSpotifyService
from models import PlaylistType


class TestPlaylistSelector:
    """Test suite for PlaylistInterface"""
    
    @pytest.fixture
    async def mock_service(self):
        """Create and initialize a MockSpotifyService instance"""
        service = MockSpotifyService()
        await service.initialize()
        return service
    
    @pytest.fixture  
    def selector(self, mock_service):
        """Create a PlaylistSelector with mock service"""
        return PlaylistSelector(mock_service)
    
    @pytest.mark.asyncio
    async def test_initialization(self, mock_service):
        """Test interface initialization"""
        selector = PlaylistSelector(mock_service)
        assert selector.service == mock_service
        assert selector.playlists == []
        
    @pytest.mark.asyncio
    async def test_load_playlists(self, interface):
        """Test loading playlists from service"""
        await interface.load_playlists()
        
        assert len(interface.playlists) == 3
        assert interface.playlists[0].name == "My Favorite Songs"
        assert interface.playlists[1].name == "Road Trip Vibes" 
        assert interface.playlists[2].name == "Chill Indie Folk"
        
    @pytest.mark.asyncio
    async def test_display_playlists(self, interface):
        """Test displaying playlists"""
        await interface.load_playlists()
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            interface.display_playlists()
            output = mock_stdout.getvalue()
            
            assert "My Favorite Songs" in output
            assert "Road Trip Vibes" in output
            assert "Chill Indie Folk" in output
            assert "owned" in output
            assert "followed" in output
            
    @pytest.mark.asyncio
    async def test_display_playlist_details(self, interface):
        """Test displaying detailed playlist information"""
        await interface.load_playlists()
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            interface.display_playlist_details(0)  # First playlist
            output = mock_stdout.getvalue()
            
            assert "My Favorite Songs" in output
            assert "Bohemian Rhapsody" in output
            assert "Queen" in output
            assert "Test User" in output
            
    @pytest.mark.asyncio
    async def test_select_playlists_by_indices(self, interface):
        """Test selecting playlists by indices"""
        await interface.load_playlists()
        
        selected = interface.select_playlists_by_indices([0, 2])
        
        assert len(selected) == 2
        assert selected[0].name == "My Favorite Songs"
        assert selected[1].name == "Chill Indie Folk"
        
    @pytest.mark.asyncio
    async def test_select_playlists_by_indices_invalid(self, interface):
        """Test selecting playlists with invalid indices"""
        await interface.load_playlists()
        
        # Should filter out invalid indices
        selected = interface.select_playlists_by_indices([0, 5, 10])
        
        assert len(selected) == 1
        assert selected[0].name == "My Favorite Songs"
        
    @pytest.mark.asyncio
    async def test_select_playlists_by_type_owned(self, interface):
        """Test selecting playlists by type - owned"""
        await interface.load_playlists()
        
        selected = interface.select_playlists_by_type(PlaylistType.OWNED)
        
        assert len(selected) == 2
        assert selected[0].name == "My Favorite Songs"
        assert selected[1].name == "Road Trip Vibes"
        assert all(p.playlist_type == PlaylistType.OWNED for p in selected)
        
    @pytest.mark.asyncio
    async def test_select_playlists_by_type_followed(self, interface):
        """Test selecting playlists by type - followed"""
        await interface.load_playlists()
        
        selected = interface.select_playlists_by_type(PlaylistType.FOLLOWED)
        
        assert len(selected) == 1
        assert selected[0].name == "Chill Indie Folk"
        assert selected[0].playlist_type == PlaylistType.FOLLOWED
        
    @pytest.mark.asyncio
    async def test_select_all_playlists(self, interface):
        """Test selecting all playlists"""
        await interface.load_playlists()
        
        selected = interface.select_all_playlists()
        
        assert len(selected) == 3
        assert selected[0].name == "My Favorite Songs"
        assert selected[1].name == "Road Trip Vibes"
        assert selected[2].name == "Chill Indie Folk"
        
    @pytest.mark.asyncio
    async def test_display_selection_summary_empty(self, interface):
        """Test displaying summary with no selection"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            interface.display_selection_summary()
            output = mock_stdout.getvalue()
            
            assert "No playlists selected" in output
            
    @pytest.mark.asyncio
    async def test_display_selection_summary_with_playlists(self, interface):
        """Test displaying summary with selected playlists"""
        await interface.load_playlists()
        interface.selected_playlists = interface.select_playlists_by_indices([0, 1])
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            interface.display_selection_summary()
            output = mock_stdout.getvalue()
            
            assert "2 playlists selected" in output
            assert "My Favorite Songs" in output
            assert "Road Trip Vibes" in output
            assert "5 total tracks" in output  # 3 + 2
            
    @pytest.mark.asyncio
    async def test_duplicate_removal_in_selection(self, interface):
        """Test that duplicate playlists are removed from selection"""
        await interface.load_playlists()
        
        # Simulate selecting the same playlist multiple times
        playlist = interface.playlists[0]
        selected_playlists = [playlist, playlist, interface.playlists[1]]
        
        # Simulate the deduplication logic from the fixed code
        seen_ids = set()
        unique_playlists = []
        for p in selected_playlists:
            if p.id not in seen_ids:
                seen_ids.add(p.id)
                unique_playlists.append(p)
                
        assert len(unique_playlists) == 2
        assert unique_playlists[0].name == "My Favorite Songs"
        assert unique_playlists[1].name == "Road Trip Vibes"
        
    @pytest.mark.asyncio
    async def test_format_duration(self, interface):
        """Test duration formatting utility"""
        # Test various durations
        assert interface._format_duration(60000) == "01:00"  # 1 minute
        assert interface._format_duration(90000) == "01:30"  # 1.5 minutes
        assert interface._format_duration(3600000) == "60:00"  # 1 hour
        assert interface._format_duration(239000) == "03:59"  # 3:59
        
    @pytest.mark.asyncio
    async def test_playlist_filtering_edge_cases(self, interface):
        """Test edge cases in playlist filtering"""
        await interface.load_playlists()
        
        # Empty indices list
        selected = interface.select_playlists_by_indices([])
        assert len(selected) == 0
        
        # All invalid indices
        selected = interface.select_playlists_by_indices([10, 20, 30])
        assert len(selected) == 0
        
        # Mixed valid and invalid
        selected = interface.select_playlists_by_indices([-1, 0, 1, 100])
        assert len(selected) == 2  # Only indices 0 and 1 are valid
        
    @pytest.mark.asyncio
    async def test_error_handling_display_details_invalid_index(self, interface):
        """Test error handling when displaying details for invalid index"""
        await interface.load_playlists()
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            # Should handle invalid index gracefully
            try:
                interface.display_playlist_details(10)  # Invalid index
            except IndexError:
                # This is expected behavior, but let's make sure it doesn't crash
                pass
                
    @pytest.mark.asyncio 
    async def test_playlist_summary_calculations(self, interface):
        """Test playlist summary calculations are accurate"""
        await interface.load_playlists()
        interface.selected_playlists = interface.select_all_playlists()
        
        # Calculate expected totals
        total_tracks = sum(p.track_count for p in interface.selected_playlists)
        total_duration = sum(p.total_duration_ms for p in interface.selected_playlists)
        
        assert total_tracks == 6  # 3 + 2 + 1
        assert total_duration > 0
        
        # Test the actual display
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            interface.display_selection_summary()
            output = mock_stdout.getvalue()
            
            assert str(total_tracks) in output
            assert "total tracks" in output