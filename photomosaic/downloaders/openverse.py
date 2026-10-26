"""
Openverse open-license image downloader.
"""
from typing import List, Optional, Any
import os
import requests
from photomosaic.downloaders.base import BaseDownloader


class OpenverseDownloader(BaseDownloader):
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        super().__init__("Openverse")
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

        url = "https://api.openverse.org/v1/images/"
        params = {"q": query, "page_size": min(limit, 50)}

        try:
            res = requests.get(url, params=params, headers=self.headers, timeout=15)
            if res.status_code == 200:
                results = res.json().get("results", [])
                total = len(results)

                for idx, item in enumerate(results):
                    img_id = item.get("id")
                    img_url = item.get("thumbnail") or item.get("url")
                    if not img_url:
                        continue

                    out_path = os.path.join(output_dir, f"openverse_{img_id}.jpg")
                    try:
                        r = requests.get(img_url, headers=self.headers, timeout=15)
                        if r.status_code == 200:
                            with open(out_path, "wb") as f:
                                f.write(r.content)
                            downloaded.append(out_path)
                    except Exception:
                        continue

                    if progress_callback and total > 0:
                        progress_callback(((idx + 1) / total) * 100.0)
        except Exception:
            pass

        return downloaded
