"""
Wikimedia Commons image downloader.
"""
from typing import List, Optional, Any
import os
import requests
from photomosaic.downloaders.base import BaseDownloader


class WikimediaDownloader(BaseDownloader):
    def __init__(self):
        super().__init__("Wikimedia Commons")
        self.headers = {"User-Agent": "PhotomosaicGenerator/2.0 (contact@example.com)"}

    def download_by_theme(
        self,
        query: str,
        output_dir: str,
        limit: int = 50,
        progress_callback: Optional[Any] = None
    ) -> List[str]:
        os.makedirs(output_dir, exist_ok=True)
        downloaded = []

        url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": f"filetype:bitmap {query}",
            "gsrnamespace": "6",
            "gsrlimit": min(limit, 50),
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": "300",
            "format": "json"
        }

        try:
            res = requests.get(url, params=params, headers=self.headers, timeout=15)
            if res.status_code == 200:
                pages = res.json().get("query", {}).get("pages", {})
                items = list(pages.values())
                total = len(items)

                for idx, page in enumerate(items):
                    imageinfo = page.get("imageinfo", [])
                    if not imageinfo:
                        continue

                    thumb_url = imageinfo[0].get("thumburl") or imageinfo[0].get("url")
                    if not thumb_url:
                        continue

                    filename = f"wikimedia_{page.get('pageid')}.jpg"
                    out_path = os.path.join(output_dir, filename)

                    try:
                        r = requests.get(thumb_url, headers=self.headers, timeout=15)
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
