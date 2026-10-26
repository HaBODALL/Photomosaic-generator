"""
Connector for WebDAV / Nextcloud photo repositories.
"""
from typing import List, Dict, Any, Optional
import os
import requests
from xml.etree import ElementTree as ET
from photomosaic.connectors.base import BaseConnector


class WebDAVConnector(BaseConnector):
    def __init__(self, webdav_url: str, username: Optional[str] = None, password: Optional[str] = None):
        super().__init__("WebDAV")
        self.webdav_url = webdav_url.rstrip("/")
        self.auth = (username, password) if username and password else None

    def test_connection(self) -> bool:
        try:
            res = requests.request("PROPFIND", self.webdav_url, auth=self.auth, headers={"Depth": "0"}, timeout=10)
            return res.status_code in [200, 207]
        except Exception:
            return False

    def list_photos(self, limit: int = 100) -> List[Dict[str, Any]]:
        photos = []
        try:
            body = """<?xml version="1.0" encoding="utf-8" ?>
            <D:propfind xmlns:D="DAV:">
                <D:prop>
                    <D:displayname/>
                    <D:getcontenttype/>
                </D:prop>
            </D:propfind>"""
            res = requests.request("PROPFIND", self.webdav_url, auth=self.auth, headers={"Depth": "1"}, data=body, timeout=15)
            if res.status_code in [200, 207]:
                root = ET.fromstring(res.content)
                for response in root.findall("{DAV:}response"):
                    href = response.find("{DAV:}href").text
                    propstat = response.find("{DAV:}propstat")
                    if propstat is not None:
                        prop = propstat.find("{DAV:}prop")
                        if prop is not None:
                            ctype = prop.find("{DAV:}getcontenttype")
                            if ctype is not None and ctype.text and ctype.text.startswith("image/"):
                                photos.append({"href": href, "name": os.path.basename(href)})
                                if len(photos) >= limit:
                                    break
        except Exception:
            pass
        return photos

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
            href = item.get("href")
            name = item.get("name")
            if not href or not name:
                continue

            if href.startswith("http"):
                file_url = href
            else:
                # Relative path join
                base_host = "/".join(self.webdav_url.split("/")[:3])
                file_url = f"{base_host}{href}"

            out_file = os.path.join(output_dir, f"webdav_{name}")

            try:
                r = requests.get(file_url, auth=self.auth, timeout=15)
                if r.status_code == 200:
                    with open(out_file, "wb") as f:
                        f.write(r.content)
                    downloaded.append(out_file)
            except Exception:
                continue

            if progress_callback and total > 0:
                progress_callback(((idx + 1) / total) * 100.0)

        return downloaded
