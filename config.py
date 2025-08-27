import os
from typing import Optional
from pathlib import Path
import json


def load_env_file(env_path: str = ".env") -> None:
    """Load environment variables from .env file"""
    env_file = Path(env_path)
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")  # Remove quotes
                    os.environ[key] = value


class SpotifyConfig:
    """Configuration management for Spotify API credentials"""
    
    def __init__(self, config_file: str = "spotify_config.json"):
        self.config_file = Path(config_file)
        self.client_id: Optional[str] = None
        self.client_secret: Optional[str] = None
        self.redirect_uri: str = "http://127.0.0.1:8000/callback"
        self.scopes = [
            "playlist-read-private",
            "playlist-read-collaborative", 
            "user-read-private",
            "user-read-email"
        ]
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file or environment variables"""
        # Load .env file first
        load_env_file()
        
        # Try to load from environment variables first
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        
        # Check for redirect URI in environment
        env_redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
        if env_redirect_uri:
            self.redirect_uri = env_redirect_uri
        
        # Override with config file if it exists
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    self.client_id = config_data.get("client_id", self.client_id)
                    self.client_secret = config_data.get("client_secret", self.client_secret)
                    self.redirect_uri = config_data.get("redirect_uri", self.redirect_uri)
                    self.scopes = config_data.get("scopes", self.scopes)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Warning: Could not load config file: {e}")
    
    def save_config(self, client_id: str, client_secret: str) -> None:
        """Save configuration to file"""
        config_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": self.redirect_uri,
            "scopes": self.scopes
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Update instance variables
        self.client_id = client_id
        self.client_secret = client_secret
    
    def is_configured(self) -> bool:
        """Check if all required configuration is present"""
        return bool(self.client_id and self.client_secret)
    
    def get_scope_string(self) -> str:
        """Get scopes as space-separated string"""
        return " ".join(self.scopes)
    
    def setup_interactive(self) -> None:
        """Interactive setup for Spotify credentials"""
        print("🎵 Spotify API Configuration Setup")
        print("=" * 50)
        print("To use this application, you need to create a Spotify app at:")
        print("https://developer.spotify.com/dashboard/applications")
        print()
        print("When creating your app, set the redirect URI to:")
        print(f"  {self.redirect_uri}")
        print()
        
        client_id = input("Enter your Spotify Client ID: ").strip()
        if not client_id:
            raise ValueError("Client ID is required")
        
        client_secret = input("Enter your Spotify Client Secret: ").strip()
        if not client_secret:
            raise ValueError("Client Secret is required")
        
        # Confirm the redirect URI
        print(f"\nUsing redirect URI: {self.redirect_uri}")
        confirm = input("Is this correct? (y/N): ").strip().lower()
        if confirm == 'y':
            self.save_config(client_id, client_secret)
            print(f"✅ Configuration saved to {self.config_file}")
        else:
            custom_uri = input("Enter your custom redirect URI: ").strip()
            if custom_uri:
                self.redirect_uri = custom_uri
            self.save_config(client_id, client_secret)
            print(f"✅ Configuration saved to {self.config_file}")


class TokenManager:
    """Manage OAuth2 tokens with persistence"""
    
    def __init__(self, token_file: str = "spotify_tokens.json"):
        self.token_file = Path(token_file)
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.expires_at: Optional[float] = None
        self.load_tokens()
    
    def load_tokens(self) -> None:
        """Load tokens from file"""
        if self.token_file.exists():
            try:
                with open(self.token_file, 'r') as f:
                    token_data = json.load(f)
                    self.access_token = token_data.get("access_token")
                    self.refresh_token = token_data.get("refresh_token")
                    self.expires_at = token_data.get("expires_at")
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Warning: Could not load tokens: {e}")
    
    def save_tokens(self, access_token: str, refresh_token: str, expires_in: int) -> None:
        """Save tokens to file"""
        import time
        
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = time.time() + expires_in
        
        token_data = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at
        }
        
        with open(self.token_file, 'w') as f:
            json.dump(token_data, f, indent=2)
    
    def is_token_valid(self) -> bool:
        """Check if current access token is valid"""
        if not self.access_token or not self.expires_at:
            return False
        
        import time
        # Add 5 minute buffer
        return time.time() < (self.expires_at - 300)
    
    def has_refresh_token(self) -> bool:
        """Check if refresh token is available"""
        return bool(self.refresh_token)
    
    def clear_tokens(self) -> None:
        """Clear all stored tokens"""
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None
        
        if self.token_file.exists():
            self.token_file.unlink()