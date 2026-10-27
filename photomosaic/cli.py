"""
CLI interface for Photomosaic generator.
"""
import argparse
import os
import cv2

from photomosaic.core.pool import TilePool
from photomosaic.core.engine import generate_mosaic_image, generate_mosaic_video
from photomosaic.downloaders.wikimedia import WikimediaDownloader
from photomosaic.downloaders.archive_org import ArchiveOrgDownloader
from photomosaic.downloaders.openverse import OpenverseDownloader
from photomosaic.downloaders.picsum import PicsumDownloader


def main():
    parser = argparse.ArgumentParser("photomosaic-cli", description="Generate photomosaics for images and videos.")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Image command
    img_parser = subparsers.add_parser("image", help="Generate photomosaic from image")
    img_parser.add_argument("--input", "-i", type=str, required=True, help="Input image path")
    img_parser.add_argument("--output", "-o", type=str, required=True, help="Output image path")
    img_parser.add_argument("--pool", "-p", type=str, default="image_pool", help="Image pool directory")
    img_parser.add_argument("--stride", "-s", type=int, default=30, help="Tile size in pixels")
    img_parser.add_argument("--color_space", type=str, default="lab", choices=["lab", "bgr"], help="Color space")
    img_parser.add_argument("--sub_grid", type=int, default=2, help="Sub-grid quadrant divisions")
    img_parser.add_argument("--anti_repetition", type=int, default=0, help="Anti-repetition threshold")
    img_parser.add_argument("--overlay_ratio", type=float, default=0.0, help="Overlay blending ratio")

    # Video command
    vid_parser = subparsers.add_parser("video", help="Generate photomosaic from video")
    vid_parser.add_argument("--input", "-i", type=str, required=True, help="Input video path")
    vid_parser.add_argument("--output", "-o", type=str, required=True, help="Output video path")
    vid_parser.add_argument("--pool", "-p", type=str, default="image_pool", help="Image pool directory")
    vid_parser.add_argument("--stride", "-s", type=int, default=20, help="Tile size in pixels")
    vid_parser.add_argument("--fps", type=int, default=0, help="Output FPS")
    vid_parser.add_argument("--color_space", type=str, default="lab", choices=["lab", "bgr"], help="Color space")
    vid_parser.add_argument("--sub_grid", type=int, default=2, help="Sub-grid quadrant divisions")
    vid_parser.add_argument("--anti_repetition", type=int, default=0, help="Anti-repetition threshold")
    vid_parser.add_argument("--overlay_ratio", type=float, default=0.0, help="Overlay blending ratio")

    # Download command
    dl_parser = subparsers.add_parser("download", help="Download images by keyword/theme")
    dl_parser.add_argument("--theme", "-t", type=str, default="random", help="Search theme or keyword")
    dl_parser.add_argument("--output", "-o", type=str, default="image_pool", help="Output directory")
    dl_parser.add_argument("--source", type=str, default="picsum", choices=["picsum", "wikimedia", "archive", "openverse"], help="Provider")
    dl_parser.add_argument("--limit", type=int, default=50, help="Number of images to download")

    args = parser.parse_args()

    if args.command == "image":
        img = cv2.imread(args.input)
        if img is None:
            raise FileNotFoundError(f"Cannot read image: {args.input}")

        pool = TilePool(
            tile_size=(args.stride, args.stride),
            color_space=args.color_space,
            sub_grid=args.sub_grid,
            anti_repetition_threshold=args.anti_repetition
        )
        pool.load_from_directory(args.pool)

        res = generate_mosaic_image(img, pool, stride=args.stride, overlay_ratio=args.overlay_ratio)
        cv2.imwrite(args.output, res)
        print(f"Photomosaic image created: {args.output}")

    elif args.command == "video":
        pool = TilePool(
            tile_size=(args.stride, args.stride),
            color_space=args.color_space,
            sub_grid=args.sub_grid,
            anti_repetition_threshold=args.anti_repetition
        )
        pool.load_from_directory(args.pool)

        generate_mosaic_video(
            input_path=args.input,
            output_path=args.output,
            pool=pool,
            stride=args.stride,
            fps=args.fps,
            overlay_ratio=args.overlay_ratio
        )
        print(f"Photomosaic video created: {args.output}")

    elif args.command == "download":
        if args.source == "picsum":
            downloader = PicsumDownloader()
        elif args.source == "wikimedia":
            downloader = WikimediaDownloader()
        elif args.source == "archive":
            downloader = ArchiveOrgDownloader()
        else:
            downloader = OpenverseDownloader()

        paths = downloader.download_by_theme(args.theme, args.output, limit=args.limit)
        print(f"Downloaded {len(paths)} images to {args.output}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
