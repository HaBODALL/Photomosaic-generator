"""
Legacy video2video.py compatibility entry point.
"""
import argparse
from photomosaic.core.pool import TilePool
from photomosaic.core.engine import generate_mosaic_video


def get_args():
    parser = argparse.ArgumentParser("Photomosaic Video Generator")
    parser.add_argument("--input", type=str, default="data/input.mp4", help="Path to input video")
    parser.add_argument("--output", type=str, default="data/output.mp4", help="Path to output video")
    parser.add_argument("--pool", type=str, default="image_pool", help="Path to directory containing component images")
    parser.add_argument("--stride", type=int, default=20, help="size of each component image")
    parser.add_argument("--fps", type=int, default=0, help="frame per second")
    parser.add_argument("--overlay_ratio", type=float, default=0.0, help="Overlay blending ratio")
    parser.add_argument("--pip_overlay", type=float, default=0.2, help="PIP Picture-in-Picture ratio")
    parser.add_argument("--color_space", type=str, default="lab", choices=["lab", "bgr"], help="Color space")
    parser.add_argument("--sub_grid", type=int, default=2, help="Sub-grid divisions")
    parser.add_argument("--anti_repetition", type=int, default=0, help="Anti-repetition threshold")
    args = parser.parse_args()
    return args


def main():
    opt = get_args()
    pool = TilePool(
        tile_size=(opt.stride, opt.stride),
        color_space=opt.color_space,
        sub_grid=opt.sub_grid,
        anti_repetition_threshold=opt.anti_repetition
    )
    pool.load_from_directory(opt.pool)

    generate_mosaic_video(
        input_path=opt.input,
        output_path=opt.output,
        pool=pool,
        stride=opt.stride,
        fps=opt.fps,
        overlay_ratio=opt.overlay_ratio,
        pip_overlay=opt.pip_overlay
    )
    print(f"Photomosaic video created successfully: {opt.output}")


if __name__ == "__main__":
    main()
