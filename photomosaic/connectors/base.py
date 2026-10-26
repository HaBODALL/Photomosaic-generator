"""
Base connector class interface for photo libraries.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os
import requests


class BaseConnector(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def test_connection(self) -> bool:
        """Test if API endpoint and credentials are valid."""
        pass

    @abstractmethod
    def list_photos(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List available photos metadata."""
        pass

    @abstractmethod
    def download_photos(
        self,
        output_dir: str,
        limit: int = 100,
        progress_callback: Optional[Any] = None
    ) -> List[str]:
        """
        Download photos to target directory.
        Returns list of local file paths.
        """
        pass
