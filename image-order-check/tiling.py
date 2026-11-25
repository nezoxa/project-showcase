"""Split an image into overlapping crops and project their detections."""

from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(frozen=True)
class Tile:
    crop: tuple[int, int, int, int]
    core: tuple[int, int, int, int]


def _axis_starts(total: int, tile: int, overlap: float) -> list[int]:
    if tile >= total:
        return [0]
    step = max(1, int(tile * (1 - overlap)))
    return list(range(0, total, step))


def _core_bounds(starts: list[int], tile: int, total: int) -> list[tuple[int, int]]:
    """Split each overlap band at its midpoint into disjoint ownership intervals."""
    bounds: list[tuple[int, int]] = []
    for i, start in enumerate(starts):
        lo = start if i == 0 else (starts[i - 1] + start + tile) // 2
        hi = total if i == len(starts) - 1 else (start + starts[i + 1] + tile) // 2
        bounds.append((min(lo, total), min(hi, total)))
    return bounds


def iter_tiles(width: int, height: int, *, tile_size: int, overlap: float) -> Iterator[Tile]:
    if min(width, height, tile_size) <= 0 or not 0 <= overlap < 1:
        raise ValueError("Dimensions must be positive and overlap must be in [0, 1).")

    xs = _axis_starts(width, tile_size, overlap)
    ys = _axis_starts(height, tile_size, overlap)
    x_cores = _core_bounds(xs, tile_size, width)
    y_cores = _core_bounds(ys, tile_size, height)

    for y, (ylo, yhi) in zip(ys, y_cores):
        for x, (xlo, xhi) in zip(xs, x_cores):
            if xlo == xhi or ylo == yhi:
                continue
            yield Tile(
                crop=(x, y, min(width, x + tile_size), min(height, y + tile_size)),
                core=(xlo, ylo, xhi, yhi),
            )


def project_box(
    tile: Tile,
    box: tuple[float, float, float, float],
    *,
    width: int,
    height: int,
) -> tuple[float, float, float, float] | None:
    """Keep a box whose center belongs to this crop, then normalize its coordinates."""
    x, y, _, _ = tile.crop
    xlo, ylo, xhi, yhi = tile.core
    bx1, by1, bx2, by2 = box
    cx, cy = x + (bx1 + bx2) / 2, y + (by1 + by2) / 2
    if not (xlo <= cx < xhi and ylo <= cy < yhi):
        return None

    return (bx1 + x) / width, (by1 + y) / height, (bx2 + x) / width, (by2 + y) / height
