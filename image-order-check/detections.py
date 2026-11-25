"""Geometry for normalized (x1, y1, x2, y2) detection boxes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DetectedInstance:
    confidence: float
    bbox: tuple[float, float, float, float] | None


def iou(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0.0:
        return 0.0
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def dedupe_boxes(
    instances: list[DetectedInstance], *, merge_iou: float
) -> list[DetectedInstance]:
    """Greedy IoU suppression across *all* boxes on one photo.

    The detector's own NMS removes same-class duplicates; this removes cross-prompt
    duplicates (one pack matched by both "box" and "package"). Instances without a bbox are
    kept as-is (nothing to compare). Higher-confidence boxes win.
    """

    boxed = [i for i in instances if i.bbox is not None]
    unboxed = [i for i in instances if i.bbox is None]
    boxed.sort(key=lambda i: -i.confidence)

    kept: list[DetectedInstance] = []
    for cand in boxed:
        assert cand.bbox is not None
        if any(iou(cand.bbox, k.bbox) > merge_iou for k in kept if k.bbox is not None):
            continue
        kept.append(cand)
    return kept + unboxed
