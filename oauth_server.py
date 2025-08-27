import asyncio
import urllib.parse
import webbrowser
from typing import Optional, Dict, Any
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from config import SpotifyConfig, TokenManager


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth2 callback"""
    
    def do_GET(self):
        """Handle GET request to callback URL"""
        # Parse the callback URL
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Store the authorization code or error
        if 'code' in query_params:
            self.server.auth_code = query_params['code'][0]
            self.server.auth_state = query_params.get('state', [None])[0]
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            success_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Spotify Authentication Success</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    .success { color: #1DB954; font-size: 24px; margin-bottom: 20px; }
                    .message { color: #333; font-size: 16px; }
                </style>
            </head>
            <body>
                <div class="success">✅ Authentication Successful!</div>
                <div class="message">
                    You have successfully authenticated with Spotify.<br>
                    You can now close this window and return to your application.
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(success_html.encode('utf-8'))
            
        elif 'error' in query_params:
            self.server.auth_error = query_params['error'][0]
            
            # Send error response
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            error_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Spotify Authentication Error</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    .error { color: #e74c3c; font-size: 24px; margin-bottom: 20px; }
                    .message { color: #333; font-size: 16px; }
                </style>
            </head>
            <body>
                <div class="error">❌ Authentication Failed</div>
                <div class="message">
                    There was an error during authentication.<br>
                    Please try again or check your Spotify app configuration.
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(error_html.encode('utf-8'))
        
        # Signal that we've received a response
        self.server.callback_received = True
    
    def log_message(self, format, *args):
        """Suppress log messages"""
        pass


class SpotifyOAuthServer:
    """OAuth2 server for handling Spotify authentication"""
    
    def __init__(self, config: SpotifyConfig):
        self.config = config
        self.server: Optional[HTTPServer] = None
        self.server_thread: Optional[threading.Thread] = None
        
    def start_server(self, port: int = 8000) -> None:
        """Start the callback server"""
        server_address = ('127.0.0.1', port)
        self.server = HTTPServer(server_address, CallbackHandler)
        
        # Add attributes to store callback data
        self.server.auth_code = None
        self.server.auth_error = None
        self.server.auth_state = None
        self.server.callback_received = False
        
        # Start server in a separate thread
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        print(f"🔄 OAuth callback server started on {server_address[0]}:{server_address[1]}")
    
    def stop_server(self) -> None:
        """Stop the callback server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=1.0)
        
        print("⏹️  OAuth callback server stopped")
    
    def get_authorization_url(self) -> str:
        """Generate the Spotify authorization URL"""
        import secrets
        import base64
        
        # Generate state parameter for security
        state = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        
        auth_params = {
            'client_id': self.config.client_id,
            'response_type': 'code',
            'redirect_uri': self.config.redirect_uri,
            'scope': self.config.get_scope_string(),
            'state': state,
            'show_dialog': 'true'  # Always show the dialog for clarity
        }
        
        auth_url = 'https://accounts.spotify.com/authorize?' + urllib.parse.urlencode(auth_params)
        self.expected_state = state
        
        return auth_url
    
    def wait_for_callback(self, timeout: int = 300) -> Optional[str]:
        """Wait for the OAuth callback and return authorization code"""
        if not self.server:
            raise Exception("Server not started")
        
        start_time = time.time()
        
        while not self.server.callback_received:
            if time.time() - start_time > timeout:
                raise TimeoutError("OAuth callback timeout")
            
            time.sleep(0.1)
        
        # Check for errors
        if hasattr(self.server, 'auth_error') and self.server.auth_error:
            raise Exception(f"OAuth error: {self.server.auth_error}")
        
        # Verify state parameter
        if hasattr(self, 'expected_state') and self.server.auth_state != self.expected_state:
            raise Exception("State parameter mismatch - possible CSRF attack")
        
        return self.server.auth_code
    
    def exchange_code_for_tokens(self, auth_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens"""
        token_url = 'https://accounts.spotify.com/api/token'
        
        token_data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.config.redirect_uri,
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(token_url, data=token_data, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Token exchange failed: {response.text}")
        
        return response.json()
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        token_url = 'https://accounts.spotify.com/api/token'
        
        token_data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(token_url, data=token_data, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Token refresh failed: {response.text}")
        
        return response.json()


class SpotifyAuthenticator:
    """High-level Spotify authentication manager"""
    
    def __init__(self, config: SpotifyConfig, token_manager: TokenManager):
        self.config = config
        self.token_manager = token_manager
        self.oauth_server = SpotifyOAuthServer(config)
    
    async def authenticate(self) -> bool:
        """Perform full OAuth2 authentication flow"""
        try:
            # Check if we have a valid token
            if self.token_manager.is_token_valid():
                print("✅ Using existing valid access token")
                return True
            
            # Try to refresh if we have a refresh token
            if self.token_manager.has_refresh_token():
                print("🔄 Refreshing access token...")
                if await self._refresh_token():
                    return True
                else:
                    print("⚠️  Token refresh failed, starting new authentication flow")
            
            # Start new authentication flow
            print("🚀 Starting OAuth2 authentication flow...")
            return await self._new_authentication()
            
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
    
    async def _refresh_token(self) -> bool:
        """Refresh access token"""
        try:
            token_response = self.oauth_server.refresh_access_token(
                self.token_manager.refresh_token
            )
            
            # Save new tokens
            self.token_manager.save_tokens(
                token_response['access_token'],
                token_response.get('refresh_token', self.token_manager.refresh_token),
                token_response['expires_in']
            )
            
            print("✅ Access token refreshed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Token refresh failed: {e}")
            return False
    
    async def _new_authentication(self) -> bool:
        """Perform new OAuth2 authentication"""
        try:
            # Start callback server
            self.oauth_server.start_server()
            
            # Generate authorization URL and open in browser
            auth_url = self.oauth_server.get_authorization_url()
            
            print("🌐 Opening Spotify authorization page in your browser...")
            print(f"If it doesn't open automatically, visit: {auth_url}")
            
            webbrowser.open(auth_url)
            
            # Wait for callback
            print("⏳ Waiting for authorization (this may take a few minutes)...")
            auth_code = self.oauth_server.wait_for_callback()
            
            if not auth_code:
                raise Exception("No authorization code received")
            
            # Exchange code for tokens
            print("🔄 Exchanging authorization code for tokens...")
            token_response = self.oauth_server.exchange_code_for_tokens(auth_code)
            
            # Save tokens
            self.token_manager.save_tokens(
                token_response['access_token'],
                token_response['refresh_token'],
                token_response['expires_in']
            )
            
            print("✅ Authentication successful!")
            return True
            
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
            
        finally:
            self.oauth_server.stop_server()
    
    def get_access_token(self) -> Optional[str]:
        """Get current valid access token"""
        if self.token_manager.is_token_valid():
            return self.token_manager.access_token
        return None