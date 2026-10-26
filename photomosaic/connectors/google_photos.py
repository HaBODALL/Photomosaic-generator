"""
Connector for Google Photos REST API.
"""
from typing import List, Dict, Any, Optional
import os
import requests
from photomosaic.connectors.base import BaseConnector


class GooglePhotosConnector(BaseConnector):
    def __init__(self, access_token: str):
        super().__init__("GooglePhotos")
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def test_connection(self) -> bool:
        try:
            res = requests.get(
                "https://photoslibrary.googleapis.com/v1/mediaItems?pageSize=1",
                headers=self.headers,
                timeout=10
            )
            return res.status_code == 200
        except Exception:
            return False

    def list_photos(self, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            pageSize = min(limit, 100)
            res = requests.get(
                f"https://photoslibrary.googleapis.com/v1/mediaItems?pageSize={pageSize}",
                headers=self.headers,
                timeout=15
            )
            if res.status_code == 200:
                return res.json().get("mediaItems", [])
        except Exception:
            pass
        return []

    def download_photos(
        self,
        output_dir: str,
        limit: int = 100,
        progress_callback: Optional[Any] = None
    ) -> List[str]:
        os.makedirs(output_dir, exist_ok=True)
        items = self.list_photos(limit=limit)
        downloaded = []

        total = len(items)
        for idx, item in enumerate(items):
            base_url = item.get("baseUrl")
            item_id = item.get("id")
            if not base_url or not item_id:
                continue

            # Request thumbnail sizing w256-h256
            thumb_url = f"{base_url}=w256-h256"
            out_file = os.path.join(output_dir, f"gphotos_{item_id[:16]}.jpg")

            try:
                r = requests.get(thumb_url, timeout=15)
                if r.status_code == 200:
                    with open(out_file, "wb") as f:
                        f.write(r.content)
                    downloaded.append(out_file)
            except Exception:
                continue

            if progress_callback and total > 0:
                progress_callback(((idx + 1) / total) * 100.0)

        return downloaded
