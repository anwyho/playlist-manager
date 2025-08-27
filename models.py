from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class PlaylistType(Enum):
    OWNED = "owned"
    FOLLOWED = "followed"
    COLLABORATIVE = "collaborative"


class TrackType(Enum):
    TRACK = "track"
    EPISODE = "episode"
    LOCAL = "local"


@dataclass
class Artist:
    id: str
    name: str
    uri: str
    external_urls: Dict[str, str]


@dataclass
class Album:
    id: str
    name: str
    uri: str
    release_date: str
    album_type: str
    artists: List[Artist]
    images: List[Dict[str, Any]]
    external_urls: Dict[str, str]


@dataclass
class Track:
    id: str
    name: str
    uri: str
    track_type: TrackType
    duration_ms: int
    explicit: bool
    popularity: int
    preview_url: Optional[str]
    track_number: int
    disc_number: int
    artists: List[Artist]
    album: Album
    external_urls: Dict[str, str]
    isrc: Optional[str] = None
    added_at: Optional[datetime] = None
    added_by_user_id: Optional[str] = None


@dataclass
class PlaylistOwner:
    id: str
    display_name: str
    uri: str
    external_urls: Dict[str, str]


@dataclass
class Playlist:
    id: str
    name: str
    description: Optional[str]
    uri: str
    playlist_type: PlaylistType
    public: bool
    collaborative: bool
    owner: PlaylistOwner
    follower_count: int
    track_count: int
    tracks: List[Track]
    images: List[Dict[str, Any]]
    external_urls: Dict[str, str]
    snapshot_id: str
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None

    @property
    def total_duration_ms(self) -> int:
        return sum(track.duration_ms for track in self.tracks)
    
    @property
    def unique_artists(self) -> List[str]:
        artists = set()
        for track in self.tracks:
            for artist in track.artists:
                artists.add(artist.name)
        return sorted(list(artists))


@dataclass
class UserProfile:
    id: str
    display_name: str
    email: str
    country: str
    follower_count: int
    uri: str
    external_urls: Dict[str, str]
    images: List[Dict[str, Any]]
    product: str  # free, premium