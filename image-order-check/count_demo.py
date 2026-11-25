"""Run the counting geometry on synthetic tile-local detections."""

from detections import DetectedInstance, dedupe_boxes
from tiling import iter_tiles, project_box


def main() -> None:
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
    expected = 3
    print(f"Raw detections: {len(sample_detections)}")
    print(f"After checking tile ownership: {len(instances)}")
    print(f"Expected: {expected}, detected: {len(kept)}, difference: {len(kept) - expected:+d}")


if __name__ == "__main__":
    main()
