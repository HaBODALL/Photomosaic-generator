"""
Archive.org public domain image downloader.
"""
from typing import List, Optional, Any
import os
import requests
from photomosaic.downloaders.base import BaseDownloader


class ArchiveOrgDownloader(BaseDownloader):
    def __init__(self):
        super().__init__("Archive.org")
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

        url = "https://archive.org/advancedsearch.php"
        params = {
            "q": f"mediatype:image AND ({query})",
            "fl[]": "identifier",
            "rows": min(limit, 50),
            "output": "json"
        }

        try:
            res = requests.get(url, params=params, headers=self.headers, timeout=15)
            if res.status_code == 200:
                docs = res.json().get("response", {}).get("docs", [])
                total = len(docs)

                for idx, doc in enumerate(docs):
                    identifier = doc.get("identifier")
                    if not identifier:
                        continue

                    thumb_url = f"https://archive.org/services/img/{identifier}"
                    out_path = os.path.join(output_dir, f"archiveorg_{identifier}.jpg")

                    try:
                        r = requests.get(thumb_url, headers=self.headers, timeout=15)
                        if r.status_code == 200 and len(r.content) > 100:
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
