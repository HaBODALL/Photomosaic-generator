"""
Lorem Picsum downloader for rapid no-API-key image pool generation.
"""
from typing import List, Optional, Any
import os
import time
import requests
from photomosaic.downloaders.base import BaseDownloader


class PicsumDownloader(BaseDownloader):
    def __init__(self, width: int = 200, height: int = 200):
        super().__init__("Lorem Picsum")
        self.width = width
        self.height = height
        self.headers = {"User-Agent": "PhotomosaicGenerator/2.0"}

    def download_by_theme(
        self,
        query: str,
        output_dir: str,
        limit: int = 50,
        progress_callback: Optional[Any] = None
    ) -> List[str]:
        os.makedirs(output_dir, exist_ok=True)
        downloaded = []

        total = max(1, limit)
        for i in range(1, total + 1):
            url = f"https://picsum.photos/{self.width}/{self.height}?random={i}"
            out_file = os.path.join(output_dir, f"picsum_{i}.jpg")

            try:
                r = requests.get(url, headers=self.headers, timeout=10)
                if r.status_code == 200:
                    with open(out_file, "wb") as f:
                        f.write(r.content)
                    downloaded.append(out_file)
            except Exception:
                pass

            if progress_callback:
                progress_callback((i / total) * 100.0)

            time.sleep(0.05)

        return downloaded
