"""
ABOUTME: Token management for Amazon Q CLI integration
Handles automatic token export, caching, and refresh from the Amazon Q CLI
"""

import json
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class TokenManager:
    """Manages Amazon Q CLI tokens with automatic refresh and caching."""
    
    def __init__(self, cache_dir: Optional[Path] = None, cli_command: str = "q"):
        """
        Initialize token manager.
        
        Args:
            cache_dir: Directory to cache tokens (default: ~/.amazon-q-langchain)
            cli_command: CLI command to use (default: "q")
        """
        self.cli_command = cli_command
        self.cache_dir = cache_dir or Path.home() / ".amazon-q-langchain"
        self.cache_dir.mkdir(exist_ok=True)
        self.token_cache_file = self.cache_dir / "token_cache.json"
        
    def get_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.
        
        Returns:
            Valid access token string
            
        Raises:
            RuntimeError: If unable to get token from CLI
        """
        # Try to load from cache first
        cached_token = self._load_cached_token()
        if cached_token and not self._is_token_expired(cached_token):
            logger.debug("Using cached token")
            return cached_token["accessToken"]
        
        # Refresh from CLI
        logger.info("Refreshing token from Amazon Q CLI")
        return self.refresh_token()
    
    def refresh_token(self) -> str:
        """
        Force refresh token from CLI.
        
        Returns:
            Fresh access token string
            
        Raises:
            RuntimeError: If CLI command fails
        """
        try:
            # Run CLI command to export token
            result = subprocess.run(
                [self.cli_command, "user", "export-token"],
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            
            # Parse JSON response
            token_data = json.loads(result.stdout)
            
            # Add timestamp for expiration tracking
            token_data["retrieved_at"] = time.time()
            
            # Cache the token
            self._save_cached_token(token_data)
            
            logger.info("Successfully refreshed token from CLI")
            return token_data["accessToken"]
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to export token from CLI: {e.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse token JSON: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except subprocess.TimeoutExpired:
            error_msg = "CLI command timed out"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def _load_cached_token(self) -> Optional[Dict[str, Any]]:
        """Load token from cache file."""
        try:
            if self.token_cache_file.exists():
                with open(self.token_cache_file, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load cached token: {e}")
        return None
    
    def _save_cached_token(self, token_data: Dict[str, Any]) -> None:
        """Save token to cache file."""
        try:
            with open(self.token_cache_file, 'w') as f:
                json.dump(token_data, f, indent=2)
        except IOError as e:
            logger.warning(f"Failed to save token cache: {e}")
    
    def _is_token_expired(self, token_data: Dict[str, Any]) -> bool:
        """
        Check if cached token is expired.
        
        We assume tokens expire after 1 hour and refresh proactively
        after 50 minutes to avoid mid-request expiration.
        """
        retrieved_at = token_data.get("retrieved_at", 0)
        age_seconds = time.time() - retrieved_at
        
        # Refresh after 50 minutes (3000 seconds)
        return age_seconds > 3000
    
    def clear_cache(self) -> None:
        """Clear the token cache."""
        try:
            if self.token_cache_file.exists():
                self.token_cache_file.unlink()
                logger.info("Token cache cleared")
        except IOError as e:
            logger.warning(f"Failed to clear token cache: {e}")
    
    def is_cli_available(self) -> bool:
        """Check if the Amazon Q CLI is available."""
        try:
            result = subprocess.run(
                [self.cli_command, "--version"],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
