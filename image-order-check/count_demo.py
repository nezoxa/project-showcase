"""Compare a synthetic detection result with the expected order count."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Box:
    left: int
    top: int
    right: int
    bottom: int
    confidence: float

    @property
    def area(self) -> int:
        return (self.right - self.left) * (self.bottom - self.top)

    def overlap(self, other: "Box") -> float:
        width = max(0, min(self.right, other.right) - max(self.left, other.left))
        height = max(0, min(self.bottom, other.bottom) - max(self.top, other.top))
        intersection = width * height
        return intersection / (self.area + other.area - intersection)


def count_objects(boxes: list[Box], threshold: float = 0.5) -> int:
    kept = []
    for box in sorted(boxes, key=lambda item: item.confidence, reverse=True):
        if all(box.overlap(other) < threshold for other in kept):
            kept.append(box)
    return len(kept)


if __name__ == "__main__":
    detections = [
        Box(10, 10, 40, 40, 0.95),
        Box(12, 12, 41, 41, 0.82),
        Box(60, 10, 90, 40, 0.93),
    ]
    expected = 3
    detected = count_objects(detections)
    print(f"Expected: {expected}, detected: {detected}, difference: {detected - expected:+d}")
