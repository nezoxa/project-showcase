"""Convert normalized detection boxes to one-class YOLO labels."""


def yolo_lines(boxes: list[tuple[float, ...]]) -> list[str]:
    """Convert normalized (x1, y1, x2, y2, ...) to '0 cx cy w h' lines."""

    out: list[str] = []
    for b in boxes:
        if len(b) < 4:
            continue
        x1, y1, x2, y2 = (float(v) for v in b[:4])
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        w, h = abs(x2 - x1), abs(y2 - y1)
        if w <= 0 or h <= 0:
            continue
        out.append(f"0 {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
    return out
