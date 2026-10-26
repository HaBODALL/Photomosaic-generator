"""
Tile pool indexing and search with cKDTree and anti-repetition logic.
"""
import os
import glob
from typing import List, Tuple, Optional, Union
import cv2
import numpy as np
from scipy.spatial import cKDTree

from photomosaic.core.color import extract_feature_vector


class TilePool:
    def __init__(
        self,
        tile_size: Tuple[int, int] = (30, 30),
        color_space: str = "lab",
        sub_grid: int = 2,
        anti_repetition_threshold: int = 0
    ):
        """
        Args:
            tile_size: (width, height) for normalized tile dimensions.
            color_space: "lab" or "bgr".
            sub_grid: 1 for simple mean, 2 for 2x2 quadrants feature vector.
            anti_repetition_threshold: Minimum grid cell distance required before reusing the same tile.
        """
        self.tile_size = tile_size
        self.color_space = color_space
        self.sub_grid = sub_grid
        self.anti_repetition_threshold = anti_repetition_threshold

        self.tiles: List[np.ndarray] = []
        self.tile_paths: List[str] = []
        self.feature_vectors: List[np.ndarray] = []
        self.kdtree: Optional[cKDTree] = None

        # Tracking usage positions for anti-repetition: tile_idx -> List[(grid_x, grid_y)]
        self.usage_history: dict = {}

    def add_image(self, image_bgr: np.ndarray, path: str = ""):
        """Resize and add a single tile image."""
        resized = cv2.resize(image_bgr, self.tile_size, interpolation=cv2.INTER_AREA)
        feat = extract_feature_vector(resized, color_space=self.color_space, sub_grid=self.sub_grid)

        idx = len(self.tiles)
        self.tiles.append(resized)
        self.tile_paths.append(path)
        self.feature_vectors.append(feat)
        self.usage_history[idx] = []

    def load_from_directory(self, folder_path: str, valid_extensions=("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp")):
        """Load all matching images from a folder."""
        if not os.path.isdir(folder_path):
            raise ValueError(f"Directory non-existent: {folder_path}")

        files = []
        for ext in valid_extensions:
            files.extend(glob.glob(os.path.join(folder_path, ext)))
            files.extend(glob.glob(os.path.join(folder_path, ext.upper())))

        files = sorted(list(set(files)))
        for filepath in files:
            img = cv2.imread(filepath, cv2.IMREAD_COLOR)
            if img is not None:
                self.add_image(img, path=filepath)

        self.build_index()

    def build_index(self):
        """Build or rebuild cKDTree index."""
        if self.feature_vectors:
            features_array = np.array(self.feature_vectors, dtype=np.float32)
            self.kdtree = cKDTree(features_array)

    def find_best_tile(self, target_feature: np.ndarray, grid_pos: Optional[Tuple[int, int]] = None, k_neighbors: int = 10) -> np.ndarray:
        """
        Find nearest matching tile in feature space considering anti-repetition penalties.
        """
        if self.kdtree is None or len(self.tiles) == 0:
            raise RuntimeError("Tile pool is empty or not indexed.")

        # Query top-K neighbors
        k = min(k_neighbors, len(self.tiles))
        distances, indices = self.kdtree.query(target_feature, k=k)

        if not isinstance(indices, (np.ndarray, list)):
            distances = [distances]
            indices = [indices]

        best_idx = indices[0]

        if self.anti_repetition_threshold > 0 and grid_pos is not None:
            gx, gy = grid_pos
            for dist, idx in zip(distances, indices):
                recent_positions = self.usage_history[idx]
                is_too_close = False
                for px, py in recent_positions:
                    # Chebyshev or Euclidean distance on grid
                    if max(abs(gx - px), abs(gy - py)) < self.anti_repetition_threshold:
                        is_too_close = True
                        break

                if not is_too_close:
                    best_idx = idx
                    break

        if grid_pos is not None:
            self.usage_history[best_idx].append(grid_pos)

        return self.tiles[best_idx]
