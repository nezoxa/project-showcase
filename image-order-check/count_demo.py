"""Run the counting geometry on synthetic tile-local detections."""

import argparse
from io import BytesIO
from pathlib import Path

from count_result import build_count_result
from detections import DetectedInstance, dedupe_boxes
from tiling import iter_tiles, project_box
from yolo_labels import yolo_lines


def save_preview(path: Path, width: int, height: int, detections: list[DetectedInstance]) -> None:
    from PIL import Image

    from visualize import draw_boxes

    with Image.new("RGB", (width, height), (35, 43, 52)) as canvas, BytesIO() as buffer:
        canvas.save(buffer, format="PNG")
        path.write_bytes(draw_boxes(buffer.getvalue(), detections))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, help="save a synthetic JPEG preview (requires Pillow)")
    args = parser.parse_args()

    width, height = 560, 320
    tiles = list(iter_tiles(width, height, tile_size=320, overlap=0.25))
    sample_detections = [
        (tiles[0], (271, 84, 297, 113), 0.88),  # Clipped copy from an adjacent tile.
        (tiles[1], (22, 74, 79, 125), 0.95),
        (tiles[1], (24, 75, 80, 126), 0.79),  # Lower-confidence copy in the same tile.
        (tiles[2], (35, 70, 68, 130), 0.91),
    ]

    instances: list[DetectedInstance] = []
    for tile, local_box, confidence in sample_detections:
        box = project_box(tile, local_box, width=width, height=height)
        if box is not None:
            instances.append(DetectedInstance(confidence=confidence, bbox=box))

    kept = dedupe_boxes(instances, merge_iou=0.5)
    result = build_count_result(len(kept), expected_count=3)
    print(f"Raw detections: {len(sample_detections)}")
    print(f"After checking tile ownership: {len(instances)}")
    print(f"Expected: {result.expected}, detected: {result.detected}, status: {result.status.value}")
    print("YOLO labels:")
    print("\n".join(yolo_lines([instance.bbox for instance in kept if instance.bbox is not None])))
    if args.image is not None:
        save_preview(args.image, width, height, kept)


if __name__ == "__main__":
    main()
