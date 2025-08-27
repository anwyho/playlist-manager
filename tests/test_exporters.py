import pytest
import json
import csv
import tempfile
import os
from datetime import datetime
from exporters.json_exporter import JSONExporter
from exporters.csv_exporter import CSVExporter
from services.mock_spotify import MockSpotifyService
from interface import PlaylistInterface


class TestJSONExporter:
    """Test suite for JSONExporter"""
    
    @pytest.fixture
    async def sample_playlists(self):
        """Create sample playlists for testing"""
        service = MockSpotifyService()
        await service.initialize()
        interface = PlaylistInterface(service)
        await interface.load_playlists()
        return interface.playlists
    
    def test_json_exporter_creation(self):
        """Test JSONExporter initialization"""
        exporter = JSONExporter()
        assert exporter is not None
        
    @pytest.mark.asyncio
    async def test_export_to_string(self, sample_playlists):
        """Test exporting playlists to JSON string"""
        exporter = JSONExporter()
        selected_playlists = sample_playlists[:2]  # First two playlists
        
        json_string = await exporter.export_to_string(selected_playlists)
        
        assert json_string is not None
        assert len(json_string) > 0
        
        # Parse JSON to verify structure
        data = json.loads(json_string)
        assert "export_metadata" in data
        assert "playlists" in data
        assert len(data["playlists"]) == 2
        
        # Check metadata
        metadata = data["export_metadata"]
        assert "export_date" in metadata
        assert "total_playlists" in metadata
        assert "total_tracks" in metadata
        assert metadata["total_playlists"] == 2
        assert metadata["total_tracks"] == 5  # 3 + 2
        
    @pytest.mark.asyncio
    async def test_export_to_file(self, sample_playlists):
        """Test exporting playlists to JSON file"""
        exporter = JSONExporter()
        selected_playlists = sample_playlists[:1]  # First playlist
        
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as tmp_file:
            try:
                await exporter.export_to_file(selected_playlists, tmp_file.name)
                
                # Verify file was created and contains valid JSON
                assert os.path.exists(tmp_file.name)
                
                with open(tmp_file.name, 'r') as f:
                    data = json.load(f)
                    
                assert "export_metadata" in data
                assert "playlists" in data
                assert len(data["playlists"]) == 1
                assert data["playlists"][0]["name"] == "My Favorite Songs"
                
            finally:
                # Clean up
                if os.path.exists(tmp_file.name):
                    os.unlink(tmp_file.name)
                    
    @pytest.mark.asyncio
    async def test_json_playlist_structure(self, sample_playlists):
        """Test JSON playlist structure is complete"""
        exporter = JSONExporter()
        playlist = sample_playlists[0]  # My Favorite Songs
        
        json_string = await exporter.export_to_string([playlist])
        data = json.loads(json_string)
        
        playlist_data = data["playlists"][0]
        
        # Check required fields
        required_fields = [
            "id", "name", "description", "uri", "playlist_type", "public",
            "collaborative", "owner", "follower_count", "track_count",
            "tracks", "total_duration_ms", "unique_artists", "created_at"
        ]
        
        for field in required_fields:
            assert field in playlist_data, f"Missing field: {field}"
            
        # Check tracks structure
        assert len(playlist_data["tracks"]) == 3
        track = playlist_data["tracks"][0]
        
        track_fields = [
            "id", "name", "uri", "duration_ms", "explicit", "popularity",
            "track_number", "artists", "album"
        ]
        
        for field in track_fields:
            assert field in track, f"Missing track field: {field}"
            
    @pytest.mark.asyncio
    async def test_json_export_empty_playlist_list(self):
        """Test exporting empty playlist list"""
        exporter = JSONExporter()
        
        json_string = await exporter.export_to_string([])
        data = json.loads(json_string)
        
        assert data["export_metadata"]["total_playlists"] == 0
        assert data["export_metadata"]["total_tracks"] == 0
        assert len(data["playlists"]) == 0


class TestCSVExporter:
    """Test suite for CSVExporter"""
    
    @pytest.fixture
    async def sample_playlists(self):
        """Create sample playlists for testing"""
        service = MockSpotifyService()
        await service.initialize()
        interface = PlaylistInterface(service)
        await interface.load_playlists()
        return interface.playlists
    
    def test_csv_exporter_creation(self):
        """Test CSVExporter initialization"""
        exporter = CSVExporter()
        assert exporter is not None
        
    @pytest.mark.asyncio
    async def test_export_to_string(self, sample_playlists):
        """Test exporting playlists to CSV string"""
        exporter = CSVExporter()
        selected_playlists = sample_playlists[:2]  # First two playlists
        
        csv_string = await exporter.export_to_string(selected_playlists)
        
        assert csv_string is not None
        assert len(csv_string) > 0
        
        # Check CSV structure
        lines = csv_string.strip().split('\n')
        assert len(lines) >= 6  # Header + 5 tracks (3 + 2)
        
        # Check header
        header = lines[0]
        expected_columns = [
            "playlist_name", "playlist_id", "playlist_type", "track_name",
            "track_id", "artist_name", "album_name", "duration_ms", "track_number"
        ]
        
        for column in expected_columns:
            assert column in header
            
    @pytest.mark.asyncio
    async def test_export_to_file(self, sample_playlists):
        """Test exporting playlists to CSV file"""
        exporter = CSVExporter()
        selected_playlists = sample_playlists[:1]  # First playlist
        
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.csv', delete=False) as tmp_file:
            try:
                await exporter.export_to_file(selected_playlists, tmp_file.name)
                
                # Verify file was created
                assert os.path.exists(tmp_file.name)
                
                with open(tmp_file.name, 'r') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    
                # Should have header + 3 tracks
                assert len(rows) == 4
                
                # Check header row
                header = rows[0]
                assert "playlist_name" in header
                assert "track_name" in header
                assert "artist_name" in header
                
                # Check first data row
                first_row = rows[1]
                assert first_row[0] == "My Favorite Songs"  # playlist_name
                assert "Bohemian Rhapsody" in first_row  # track_name should be somewhere
                
            finally:
                # Clean up
                if os.path.exists(tmp_file.name):
                    os.unlink(tmp_file.name)
                    
    @pytest.mark.asyncio
    async def test_csv_track_data_accuracy(self, sample_playlists):
        """Test CSV track data is accurate"""
        exporter = CSVExporter()
        playlist = sample_playlists[0]  # My Favorite Songs
        
        csv_string = await exporter.export_to_string([playlist])
        lines = csv_string.strip().split('\n')
        
        # Parse CSV
        reader = csv.DictReader(lines)
        tracks = list(reader)
        
        assert len(tracks) == 3
        
        # Check first track data
        first_track = tracks[0]
        assert first_track["track_name"] == "Bohemian Rhapsody"
        assert first_track["artist_name"] == "Queen"
        assert first_track["album_name"] == "A Night at the Opera"
        assert int(first_track["duration_ms"]) == 354000
        assert int(first_track["track_number"]) == 1
        
    @pytest.mark.asyncio
    async def test_csv_multiple_artists_handling(self, sample_playlists):
        """Test how CSV handles tracks with multiple artists"""
        exporter = CSVExporter()
        
        # Find a track with multiple artists (if any exist in mock data)
        # For now, test with existing single-artist tracks
        csv_string = await exporter.export_to_string([sample_playlists[0]])
        
        # Ensure no errors and proper formatting
        lines = csv_string.strip().split('\n')
        reader = csv.DictReader(lines)
        tracks = list(reader)
        
        # All tracks should have artist names
        for track in tracks:
            assert len(track["artist_name"]) > 0
            
    @pytest.mark.asyncio
    async def test_csv_export_empty_playlist_list(self):
        """Test exporting empty playlist list to CSV"""
        exporter = CSVExporter()
        
        csv_string = await exporter.export_to_string([])
        
        # Should still have header
        lines = csv_string.strip().split('\n')
        assert len(lines) == 1  # Only header
        
        header = lines[0]
        assert "playlist_name" in header
        
    @pytest.mark.asyncio
    async def test_csv_special_characters(self, sample_playlists):
        """Test CSV handles special characters properly"""
        exporter = CSVExporter()
        
        # The mock data should include some special characters
        csv_string = await exporter.export_to_string(sample_playlists)
        
        # Should not crash and should be parseable
        lines = csv_string.strip().split('\n')
        reader = csv.DictReader(lines)
        tracks = list(reader)
        
        # Verify we can read all tracks without issues
        assert len(tracks) == 6  # 3 + 2 + 1 tracks total
        
        # Check that CSV properly escapes any special characters
        for track in tracks:
            # Should not have unescaped quotes or commas breaking the format
            assert track["playlist_name"] is not None
            assert track["track_name"] is not None


class TestExporterIntegration:
    """Integration tests for exporters"""
    
    @pytest.fixture
    async def full_interface(self):
        """Create interface with all playlists loaded"""
        service = MockSpotifyService()
        await service.initialize()
        interface = PlaylistInterface(service)
        await interface.load_playlists()
        return interface
    
    @pytest.mark.asyncio
    async def test_json_csv_export_consistency(self, full_interface):
        """Test that JSON and CSV exports contain consistent data"""
        selected_playlists = full_interface.playlists[:2]
        
        json_exporter = JSONExporter()
        csv_exporter = CSVExporter()
        
        json_string = await json_exporter.export_to_string(selected_playlists)
        csv_string = await csv_exporter.export_to_string(selected_playlists)
        
        # Parse both formats
        json_data = json.loads(json_string)
        csv_lines = csv_string.strip().split('\n')
        csv_reader = csv.DictReader(csv_lines)
        csv_tracks = list(csv_reader)
        
        # Count total tracks in JSON
        json_track_count = sum(len(p["tracks"]) for p in json_data["playlists"])
        
        # Should have same number of tracks
        assert json_track_count == len(csv_tracks)
        assert json_data["export_metadata"]["total_tracks"] == len(csv_tracks)
        
    @pytest.mark.asyncio
    async def test_export_with_selection(self, full_interface):
        """Test exporting with different playlist selections"""
        # Test exporting owned playlists only
        owned_playlists = full_interface.select_playlists_by_type(full_interface.playlists[0].playlist_type)
        
        json_exporter = JSONExporter()
        json_string = await json_exporter.export_to_string(owned_playlists)
        data = json.loads(json_string)
        
        # Should only include owned playlists
        for playlist in data["playlists"]:
            assert playlist["playlist_type"] == "owned"