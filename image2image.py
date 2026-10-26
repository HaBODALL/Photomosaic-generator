"""
Legacy image2image.py compatibility entry point.
"""
import argparse
import cv2
from photomosaic.core.pool import TilePool
from photomosaic.core.engine import generate_mosaic_image


def get_args():
    parser = argparse.ArgumentParser("Photomosaic Image Generator")
    parser.add_argument("--input", type=str, default="data/input.jpg", help="Path to input image")
    parser.add_argument("--output", type=str, default="data/output.jpg", help="Path to output image")
    parser.add_argument("--pool", type=str, default="image_pool", help="Path to directory containing component images")
    parser.add_argument("--stride", type=int, default=30, help="size of each component image")
    parser.add_argument("--color_space", type=str, default="lab", choices=["lab", "bgr"], help="Color space for matching")
    parser.add_argument("--sub_grid", type=int, default=2, help="Sub-grid divisions for feature vector")
    parser.add_argument("--anti_repetition", type=int, default=0, help="Anti-repetition distance threshold")
    parser.add_argument("--overlay_ratio", type=float, default=0.0, help="Overlay blending ratio")
    args = parser.parse_args()
    return args


def main():
    opt = get_args()
    input_image = cv2.imread(opt.input, cv2.IMREAD_COLOR)
    if input_image is None:
        raise FileNotFoundError(f"Input image not found: {opt.input}")

    pool = TilePool(
        tile_size=(opt.stride, opt.stride),
        color_space=opt.color_space,
        sub_grid=opt.sub_grid,
        anti_repetition_threshold=opt.anti_repetition
    )
    pool.load_from_directory(opt.pool)

    output_image = generate_mosaic_image(
        input_image,
        pool,
        stride=opt.stride,
        overlay_ratio=opt.overlay_ratio
    )
    cv2.imwrite(opt.output, output_image)
    print(f"Photomosaic created successfully: {opt.output}")


if __name__ == "__main__":
    main()
