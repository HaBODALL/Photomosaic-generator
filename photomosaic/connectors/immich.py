"""
Connector for Immich self-hosted photo management.
"""
from typing import List, Dict, Any, Optional
import os
import requests
from photomosaic.connectors.base import BaseConnector


class ImmichConnector(BaseConnector):
    def __init__(self, host_url: str, api_key: str):
        super().__init__("Immich")
        self.host_url = host_url.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "x-api-key": self.api_key,
            "Accept": "application/json"
        }

    def test_connection(self) -> bool:
        try:
            res = requests.get(f"{self.host_url}/api/server-info/ping", headers=self.headers, timeout=10)
            return res.status_code == 200 and res.json().get("res") == "pong"
        except Exception:
            return False

    def list_photos(self, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            # Search or list assets from Immich
            res = requests.post(
                f"{self.host_url}/api/search/metadata",
                headers=self.headers,
                json={"take": limit, "type": "IMAGE"},
                timeout=15
            )
            if res.status_code == 200:
                items = res.json().get("assets", {}).get("items", [])
                return items
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
            asset_id = item.get("id")
            if not asset_id:
                continue

            thumb_url = f"{self.host_url}/api/asset/file/{asset_id}?isThumbnail=true"
            out_file = os.path.join(output_dir, f"immich_{asset_id}.jpg")

            try:
                r = requests.get(thumb_url, headers=self.headers, timeout=15)
                if r.status_code == 200:
                    with open(out_file, "wb") as f:
                        f.write(r.content)
                    downloaded.append(out_file)
            except Exception:
                continue

            if progress_callback and total > 0:
                progress_callback(((idx + 1) / total) * 100.0)

        return downloaded
