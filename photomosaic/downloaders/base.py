"""
Base downloader interface for open image providers.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Any
import os


class BaseDownloader(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def download_by_theme(
        self,
        query: str,
        output_dir: str,
        limit: int = 50,
        progress_callback: Optional[Any] = None
    ) -> List[str]:
        """
        Search and download images matching query string.
        Returns list of local file paths.
        """
        pass
