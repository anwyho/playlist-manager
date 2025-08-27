from abc import ABC, abstractmethod
from typing import List, Optional
from models import Playlist, UserProfile, Track


class MusicServiceError(Exception):
    """Base exception for music service operations"""
    pass


class AuthenticationError(MusicServiceError):
    """Raised when authentication fails"""
    pass


class RateLimitError(MusicServiceError):
    """Raised when API rate limit is exceeded"""
    pass


class MusicService(ABC):
    """Abstract base class for music streaming services"""
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the music service"""
        pass
    
    @abstractmethod
    async def get_user_profile(self) -> UserProfile:
        """Get the authenticated user's profile"""
        pass
    
    @abstractmethod
    async def get_user_playlists(self, limit: Optional[int] = None) -> List[Playlist]:
        """Get all playlists for the authenticated user"""
        pass
    
    @abstractmethod
    async def get_playlist_details(self, playlist_id: str) -> Playlist:
        """Get detailed information about a specific playlist"""
        pass
    
    @abstractmethod
    async def get_playlist_tracks(self, playlist_id: str) -> List[Track]:
        """Get all tracks from a specific playlist"""
        pass
    
    @property
    @abstractmethod
    def service_name(self) -> str:
        """Name of the music service"""
        pass
    
    @property
    @abstractmethod
    def is_authenticated(self) -> bool:
        """Check if the service is currently authenticated"""
        pass


class PlaylistExporter(ABC):
    """Abstract base class for playlist export functionality"""
    
    @abstractmethod
    def export_playlist(self, playlist: Playlist, file_path: str) -> None:
        """Export a single playlist to a file"""
        pass
    
    @abstractmethod
    def export_playlists(self, playlists: List[Playlist], file_path: str) -> None:
        """Export multiple playlists to a file"""
        pass
    
    @property
    @abstractmethod
    def file_extension(self) -> str:
        """File extension for this export format"""
        pass
    
    @property
    @abstractmethod
    def format_name(self) -> str:
        """Human-readable name of the export format"""
        pass


class PlaylistMigrator(ABC):
    """Abstract base class for migrating playlists between services"""
    
    @abstractmethod
    async def migrate_playlist(
        self, 
        source_playlist: Playlist, 
        destination_service: MusicService
    ) -> Optional[str]:
        """
        Migrate a playlist from source to destination service
        Returns the new playlist ID if successful, None otherwise
        """
        pass
    
    @abstractmethod
    def calculate_migration_compatibility(
        self, 
        source_playlist: Playlist
    ) -> float:
        """
        Calculate how well a playlist can be migrated (0.0 to 1.0)
        Based on track availability, metadata completeness, etc.
        """
        pass