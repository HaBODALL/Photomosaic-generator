"""
Stock API downloaders for Unsplash, Pexels, and Pixabay.
"""
from typing import List, Optional, Any
import os
import requests
from photomosaic.downloaders.base import BaseDownloader


class UnsplashDownloader(BaseDownloader):
    def __init__(self, access_key: str):
        super().__init__("Unsplash")
        self.access_key = access_key
        self.headers = {"Authorization": f"Client-ID {self.access_key}"}

    def download_by_theme(
        self,
        query: str,
        output_dir: str,
        limit: int = 50,
        progress_callback: Optional[Any] = None
    ) -> List[str]:
        os.makedirs(output_dir, exist_ok=True)
        downloaded = []

        url = "https://api.unsplash.com/search/photos"
        params = {"query": query, "per_page": min(limit, 30)}

        try:
            res = requests.get(url, params=params, headers=self.headers, timeout=15)
            if res.status_code == 200:
                results = res.json().get("results", [])
                total = len(results)

                for idx, item in enumerate(results):
                    item_id = item.get("id")
                    urls = item.get("urls", {})
                    thumb_url = urls.get("small") or urls.get("raw")
                    if not thumb_url:
                        continue

                    out_path = os.path.join(output_dir, f"unsplash_{item_id}.jpg")
                    try:
                        r = requests.get(thumb_url, timeout=15)
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


class PexelsDownloader(BaseDownloader):
    def __init__(self, api_key: str):
        super().__init__("Pexels")
        self.api_key = api_key
        self.headers = {"Authorization": self.api_key}

    def download_by_theme(
        self,
        query: str,
        output_dir: str,
        limit: int = 50,
        progress_callback: Optional[Any] = None
    ) -> List[str]:
        os.makedirs(output_dir, exist_ok=True)
        downloaded = []

        url = "https://api.pexels.com/v1/search"
        params = {"query": query, "per_page": min(limit, 80)}

        try:
            res = requests.get(url, params=params, headers=self.headers, timeout=15)
            if res.status_code == 200:
                photos = res.json().get("photos", [])
                total = len(photos)

                for idx, item in enumerate(photos):
                    item_id = item.get("id")
                    src = item.get("src", {})
                    thumb_url = src.get("medium") or src.get("small")
                    if not thumb_url:
                        continue

                    out_path = os.path.join(output_dir, f"pexels_{item_id}.jpg")
                    try:
                        r = requests.get(thumb_url, timeout=15)
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


class PixabayDownloader(BaseDownloader):
    def __init__(self, api_key: str):
        super().__init__("Pixabay")
        self.api_key = api_key

    def download_by_theme(
        self,
        query: str,
        output_dir: str,
        limit: int = 50,
        progress_callback: Optional[Any] = None
    ) -> List[str]:
        os.makedirs(output_dir, exist_ok=True)
        downloaded = []

        url = "https://pixabay.com/api/"
        params = {"key": self.api_key, "q": query, "image_type": "photo", "per_page": min(limit, 100)}

        try:
            res = requests.get(url, params=params, timeout=15)
            if res.status_code == 200:
                hits = res.json().get("hits", [])
                total = len(hits)

                for idx, item in enumerate(hits):
                    item_id = item.get("id")
                    thumb_url = item.get("previewURL") or item.get("webformatURL")
                    if not thumb_url:
                        continue

                    out_path = os.path.join(output_dir, f"pixabay_{item_id}.jpg")
                    try:
                        r = requests.get(thumb_url, timeout=15)
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
