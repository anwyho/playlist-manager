# 🎵 Spotify Playlist Keeper

A Python application to backup and export your Spotify playlists with full metadata preservation. Perfect for creating backups before migrating to other music services like Apple Music.

## 📋 TODO List for Next Session

### High Priority - Interface Improvements
- [ ] **Implement pagination for playlist interface** - Support for 700+ playlists
  - Add pagination controls (next/previous page, jump to page)
  - Configurable page size (default: 25-50 playlists per page)
  - Search/filter by playlist name before retrieval
- [ ] **Add initial filters before retrieving playlists**
  - Filter by playlist type (owned/followed/collaborative) before API call
  - Filter by date range (created/modified within X months)
  - Filter by playlist size (minimum/maximum track count)
  - Filter by public/private status
  - Option to exclude empty playlists
- [ ] **Browse exported data functionality**
  - Add viewer/browser for JSON exports
  - Search and filter through exported playlists
  - Compare multiple exports
  - Mark playlists for import to other services

### Apple Music Integration Preparation
- [ ] **Research Apple Music API** - Analyze authentication, data models, and migration compatibility
- [ ] **Simplify exporter data model**
  - Create common/universal data structure for cross-service compatibility
  - Move service-specific attributes to sub-objects (e.g., `spotify_specific`, `apple_music_specific`)
  - Focus on ISRC codes and basic metadata for matching
- [ ] **Design migration workflow**
  - Create mapping between services for track/playlist matching
  - Handle tracks not available on target service
  - Preserve playlist order and metadata

### Technical Improvements
- [ ] **Implement smart caching system**
  - Cache playlist metadata locally (SQLite/JSON) with timestamps
  - Skip API calls for playlists fetched within last hour
  - Add `--force-refresh` CLI flag to bypass cache
  - Add `--max-cache-age` option (default: 1 hour)
  - Cache invalidation for modified playlists (track snapshot_id changes)
  - Show cache status in interface ("cached 45min ago" vs "fetching...")
- [ ] **Improve test coverage**
  - Fix mock service tests (API method alignment)
  - Add integration tests for interface pagination  
  - Add tests for export data browsing and caching
  - Test service abstraction with multiple services
- [ ] **Strengthen type annotations**
  - Add more specific typing for API responses
  - Use Protocol/TypedDict for better API contracts
  - Add runtime type validation for critical paths
- [ ] **Enhanced SQLite database support**
  - Cache playlist metadata locally for faster browsing
  - Store export history and comparison data
  - Enable offline playlist analysis
  - Track cache timestamps and invalidation rules

### User Experience Enhancements
- [ ] **Better CLI experience**
  - Add command-line arguments for batch operations
  - Progress bars for large playlist processing
  - Colorized output and better formatting
- [ ] **Export comparison tools**
  - Diff between different exports over time
  - Track playlist changes and additions
  - Generate migration recommendations

## ✨ Features

- **Complete Metadata Backup**: Preserve all playlist and track information including ISRC codes, URIs, popularity scores, and relationships
- **Interactive Selection**: Choose which playlists to backup with a user-friendly interface
- **Multiple Export Formats**: Export to JSON (full metadata) or CSV (spreadsheet-friendly)
- **OAuth2 Authentication**: Secure integration with Spotify's official API
- **Modular Architecture**: Easily extensible to support other music services
- **Mock Mode**: Test the interface without API credentials

## 🚀 Quick Start

### 1. Setup Spotify API

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications)
2. Click "Create an App"
3. Fill in your app details
4. Add redirect URI: `http://127.0.0.1:8000/callback`
5. Save and note your Client ID and Client Secret

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Credentials

**Option A: Use setup script (recommended)**
```bash
python3 setup.py
```

**Option B: Create .env file manually**
```bash
cp .env.example .env
# Edit .env with your credentials
```

**Option C: Set environment variables**
```bash
export SPOTIFY_CLIENT_ID="your_client_id"
export SPOTIFY_CLIENT_SECRET="your_client_secret"
```

### 4. Run the Application

```bash
python3 main.py
```

Select "Real Spotify API" and follow the authentication flow.

## 📖 Usage Guide

### Authentication Flow
1. The app will open your browser to Spotify's authorization page
2. Log in and grant permissions to the app
3. You'll be redirected to a success page
4. Return to the terminal to continue

### Selecting Playlists
- **View all**: See all your playlists with metadata
- **Individual selection**: Pick specific playlists by number
- **Bulk selection**: Select by type (owned/followed/collaborative)
- **Preview**: View detailed playlist information before selecting

### Export Formats

**JSON Format**
- Complete metadata preservation
- Perfect for programmatic processing
- Includes nested artist/album relationships
- Preserves all Spotify URIs and external URLs

**CSV Format**
- Spreadsheet-friendly format
- One row per track
- Includes playlist and track metadata
- Easy to analyze in Excel/Google Sheets

## 🏗️ Architecture

```
spotify-playlist-keeper/
├── models.py              # Data models (Playlist, Track, Artist, Album)
├── services/
│   ├── base.py           # Service abstractions
│   ├── mock_spotify.py   # Mock service for testing
│   └── spotify_service.py # Real Spotify API integration
├── exporters/
│   ├── json_exporter.py  # JSON export functionality
│   └── csv_exporter.py   # CSV export functionality
├── oauth_server.py       # OAuth2 callback server
├── config.py            # Configuration management
├── interface.py         # Interactive playlist selection
└── main.py             # Main application
```

### Key Design Patterns

**Service Abstraction**: Easy to add support for other music services (Apple Music, YouTube Music, etc.)

```python
class MusicService(ABC):
    @abstractmethod
    async def get_user_playlists(self) -> List[Playlist]
```

**Export Abstraction**: Simple to add new export formats

```python
class PlaylistExporter(ABC):
    @abstractmethod
    def export_playlists(self, playlists: List[Playlist], file_path: str)
```

**Rich Data Models**: Comprehensive metadata capture for future migration

```python
@dataclass
class Track:
    id: str
    name: str
    isrc: Optional[str]  # For cross-service matching
    artists: List[Artist]
    album: Album
    # ... full Spotify metadata
```

## 🔧 Configuration Options

### Environment Variables
- `SPOTIFY_CLIENT_ID`: Your app's client ID
- `SPOTIFY_CLIENT_SECRET`: Your app's client secret  
- `SPOTIFY_REDIRECT_URI`: OAuth callback URL (default: http://127.0.0.1:8000/callback)

### Scopes Required
- `playlist-read-private`: Access private playlists
- `playlist-read-collaborative`: Access collaborative playlists
- `user-read-private`: Access user profile
- `user-read-email`: Access user email

## 📊 Export Data Structure

### JSON Export
```json
{
  "export_timestamp": "2025-01-01T12:00:00",
  "total_playlists": 5,
  "playlists": [
    {
      "id": "playlist_id",
      "name": "My Playlist",
      "description": "A great playlist",
      "tracks": [
        {
          "id": "track_id",
          "name": "Song Name",
          "isrc": "USUM71234567",
          "artists": [...],
          "album": {...}
        }
      ]
    }
  ]
}
```

### CSV Columns
- Playlist metadata: ID, name, description, type, owner, etc.
- Track metadata: ID, name, duration, popularity, etc.
- Artist information: Names and IDs
- Album information: Name, release date, type
- Spotify URLs: Direct links to playlists and tracks

## 🛠️ Development

### Testing with Mock Service
```bash
python3 -c "
import asyncio
from services.mock_spotify import MockSpotifyService

async def test():
    service = MockSpotifyService()
    await service.authenticate()
    playlists = await service.get_user_playlists()
    print(f'Found {len(playlists)} playlists')

asyncio.run(test())
"
```

### Adding New Export Formats
1. Create exporter class inheriting from `PlaylistExporter`
2. Implement required methods
3. Add to `PlaylistManager.exporters` dictionary

### Adding New Music Services
1. Create service class inheriting from `MusicService`
2. Implement OAuth2 flow and API calls
3. Map API responses to common data models

## 🔒 Security Notes

- API credentials are stored in `.env` (gitignored)
- OAuth2 tokens are cached locally in `spotify_tokens.json`
- State parameter validation prevents CSRF attacks
- Tokens automatically refresh when expired

## 🤝 Contributing

This project is designed to be easily extensible:
- Add new music services (Apple Music, YouTube Music)
- Add new export formats (XML, YAML, etc.)
- Enhance playlist filtering and selection
- Improve migration compatibility scoring

## 📄 License

This project is for personal backup and migration purposes. Respect Spotify's Terms of Service and API guidelines.

## 🆘 Troubleshooting

**"Not authenticated" errors**
- Check your API credentials in `.env`
- Ensure redirect URI matches your Spotify app settings
- Try deleting `spotify_tokens.json` to force re-authentication

**"Rate limited" errors**
- The app handles rate limiting automatically
- Large libraries may take time to process
- Consider reducing the number of playlists selected

**OAuth callback issues**
- Ensure nothing else is running on port 8000
- Check your Spotify app's redirect URI setting
- Try using a different redirect URI in your `.env`

**Empty playlists**
- Some playlists may contain local files or unavailable tracks
- Check the original playlist in Spotify
- The app skips tracks that can't be accessed via API