"""
Photomosaic processing engine for images and videos with parallel processing.
"""
import os
from typing import Optional, Callable
from concurrent.futures import ProcessPoolExecutor, as_completed
import cv2
import numpy as np

from photomosaic.core.color import extract_feature_vector
from photomosaic.core.pool import TilePool


def generate_mosaic_image(
    input_image: np.ndarray,
    pool: TilePool,
    stride: int = 30,
    overlay_ratio: float = 0.0,
    progress_callback: Optional[Callable[[float], None]] = None
) -> np.ndarray:
    """
    Generate a photomosaic image from input BGR image.

    Args:
        input_image: BGR source image array.
        pool: Initialized and built TilePool.
        stride: Size of each mosaic cell in pixels.
        overlay_ratio: Blending ratio (0.0 to 1.0) of original input image over mosaic.
        progress_callback: Callback function receiving progress percentage float (0.0 to 100.0).

    Returns:
        Generated mosaic image array.
    """
    height, width, _ = input_image.shape
    cols = width // stride
    rows = height // stride

    target_w = cols * stride
    target_h = rows * stride

    # Resize input image to fit whole grid steps
    resized_input = cv2.resize(input_image, (target_w, target_h), interpolation=cv2.INTER_AREA)
    output_image = np.zeros((target_h, target_w, 3), dtype=np.uint8)

    total_cells = cols * rows
    cell_count = 0

    for j in range(rows):
        for i in range(cols):
            y_start, y_end = j * stride, (j + 1) * stride
            x_start, x_end = i * stride, (i + 1) * stride

            patch = resized_input[y_start:y_end, x_start:x_end, :]
            target_feat = extract_feature_vector(
                patch, color_space=pool.color_space, sub_grid=pool.sub_grid
            )

            best_tile = pool.find_best_tile(target_feat, grid_pos=(i, j))
            if best_tile.shape[0] != stride or best_tile.shape[1] != stride:
                best_tile = cv2.resize(best_tile, (stride, stride), interpolation=cv2.INTER_AREA)

            output_image[y_start:y_end, x_start:x_end, :] = best_tile

            cell_count += 1
            if progress_callback and (cell_count % 100 == 0 or cell_count == total_cells):
                progress_callback((cell_count / total_cells) * 100.0)

    # Optional overlay blending
    if overlay_ratio > 0.0:
        overlay_ratio = max(0.0, min(1.0, overlay_ratio))
        output_image = cv2.addWeighted(output_image, 1.0 - overlay_ratio, resized_input, overlay_ratio, 0)

    return output_image


def _process_frame_worker(args):
    """Worker function for parallel video frame processing."""
    frame_idx, frame, pool, stride, overlay_ratio = args
    mosaic_frame = generate_mosaic_image(frame, pool, stride, overlay_ratio=overlay_ratio)
    return frame_idx, mosaic_frame


def generate_mosaic_video(
    input_path: str,
    output_path: str,
    pool: TilePool,
    stride: int = 20,
    fps: int = 0,
    overlay_ratio: float = 0.0,
    pip_overlay: float = 0.2,
    num_workers: Optional[int] = None,
    progress_callback: Optional[Callable[[float], None]] = None
):
    """
    Generate a photomosaic video with multi-process frame acceleration.
    """
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open input video: {input_path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_fps = int(cap.get(cv2.CAP_PROP_FPS)) if fps == 0 else fps
    if video_fps <= 0:
        video_fps = 24

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    out = cv2.VideoWriter(output_path, fourcc, video_fps, (width, height))

    frames = []
    frame_idx = 0
    while cap.isOpened():
        flag, frame = cap.read()
        if not flag:
            break
        frames.append((frame_idx, frame, pool, stride, overlay_ratio))
        frame_idx += 1
    cap.release()

    if not frames:
        raise ValueError("No frames found in input video.")

    results = {}
    total_to_process = len(frames)
    completed = 0

    if num_workers is None:
        num_workers = min(os.cpu_count() or 1, 8)

    if num_workers <= 1:
        for item in frames:
            f_idx, m_frame = _process_frame_worker(item)
            results[f_idx] = m_frame
            completed += 1
            if progress_callback:
                progress_callback((completed / total_to_process) * 100.0)
    else:
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(_process_frame_worker, item) for item in frames]
            for future in as_completed(futures):
                f_idx, m_frame = future.result()
                results[f_idx] = m_frame
                completed += 1
                if progress_callback:
                    progress_callback((completed / total_to_process) * 100.0)

    # Write frames in sequential order
    for idx in range(total_to_process):
        blank_image = results[idx]
        if pip_overlay > 0.0:
            pip_w, pip_h = int(width * pip_overlay), int(height * pip_overlay)
            if pip_w > 0 and pip_h > 0:
                raw_frame = frames[idx][1]
                overlay = cv2.resize(raw_frame, (pip_w, pip_h), interpolation=cv2.INTER_AREA)
                blank_image[height - pip_h :, width - pip_w :, :] = overlay
        out.write(blank_image)

    out.release()
