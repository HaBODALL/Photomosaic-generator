"""
Unit and integration test suite for Photomosaic Generator.
"""
import os
import tempfile
import cv2
import numpy as np
import pytest

from photomosaic.core.color import bgr_to_lab, extract_feature_vector
from photomosaic.core.pool import TilePool
from photomosaic.core.engine import generate_mosaic_image
from photomosaic.downloaders.wikimedia import WikimediaDownloader
from photomosaic.downloaders.archive_org import ArchiveOrgDownloader
from photomosaic.connectors.immich import ImmichConnector
from photomosaic.connectors.webdav import WebDAVConnector


def test_color_extraction():
    # 10x10 red image in BGR: [0, 0, 255]
    red_img = np.zeros((10, 10, 3), dtype=np.uint8)
    red_img[:, :] = (0, 0, 255)

    lab = bgr_to_lab(red_img)
    assert lab.shape == (10, 10, 3)

    feat1 = extract_feature_vector(red_img, color_space="lab", sub_grid=1)
    assert feat1.shape == (3,)

    feat2 = extract_feature_vector(red_img, color_space="lab", sub_grid=2)
    assert feat2.shape == (12,)  # 2x2 grid * 3 channels = 12


def test_tile_pool_and_mosaic():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create 3 dummy colored tile images
        for idx, color in enumerate([(255, 0, 0), (0, 255, 0), (0, 0, 255)]):
            tile = np.zeros((30, 30, 3), dtype=np.uint8)
            tile[:, :] = color
            cv2.imwrite(os.path.join(tmpdir, f"tile_{idx}.jpg"), tile)

        pool = TilePool(tile_size=(30, 30), color_space="lab", sub_grid=2, anti_repetition_threshold=1)
        pool.load_from_directory(tmpdir)
        assert len(pool.tiles) == 3

        # Create target image 60x60
        target = np.zeros((60, 60, 3), dtype=np.uint8)
        target[:30, :30] = (255, 0, 0)
        target[:30, 30:] = (0, 255, 0)
        target[30:, :30] = (0, 0, 255)
        target[30:, 30:] = (255, 0, 0)

        mosaic = generate_mosaic_image(target, pool, stride=30)
        assert mosaic.shape == (60, 60, 3)


def test_downloaders():
    dl = WikimediaDownloader()
    assert dl.name == "Wikimedia Commons"

    archive_dl = ArchiveOrgDownloader()
    assert archive_dl.name == "Archive.org"


def test_connectors():
    immich = ImmichConnector("http://localhost:2283", "fake_key")
    assert immich.name == "Immich"
    assert immich.test_connection() is False

    dav = WebDAVConnector("http://localhost:8080")
    assert dav.name == "WebDAV"
    assert dav.test_connection() is False
