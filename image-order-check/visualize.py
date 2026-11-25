"""Draw numbered detection boxes and a count on an image."""

from __future__ import annotations

import io
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from detections import DetectedInstance

_BOX_COLOR = (46, 204, 113)
_TEXT_BG = (46, 204, 113)


def _font() -> Any:
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", 18)
    except OSError:
        return ImageFont.load_default()


def draw_boxes(image_bytes: bytes, instances: list[DetectedInstance]) -> bytes:
    with Image.open(io.BytesIO(image_bytes)) as opened:
        img = opened.convert("RGB")
    w, h = img.size
    draw = ImageDraw.Draw(img)
    font = _font()

    line = max(2, round(min(w, h) * 0.004))
    for i, inst in enumerate(instances, start=1):
        if inst.bbox is None:
            continue
        x1, y1, x2, y2 = inst.bbox
        box = (x1 * w, y1 * h, x2 * w, y2 * h)
        draw.rectangle(box, outline=_BOX_COLOR, width=line)
        label = str(i)
        tb = draw.textbbox((0, 0), label, font=font)
        tw, th = tb[2] - tb[0], tb[3] - tb[1]
        lx, ly = box[0], max(0.0, box[1] - th - 6)
        draw.rectangle((lx, ly, lx + tw + 8, ly + th + 6), fill=_TEXT_BG)
        draw.text((lx + 4, ly + 2), label, fill=(255, 255, 255), font=font)

    total = sum(1 for x in instances if x.bbox is not None)
    caption = f"Objects: {total}"
    cb = draw.textbbox((0, 0), caption, font=font)
    draw.rectangle((0, 0, cb[2] - cb[0] + 16, cb[3] - cb[1] + 12), fill=(0, 0, 0))
    draw.text((8, 4), caption, fill=(255, 255, 255), font=font)

    out = io.BytesIO()
    img.save(out, format="JPEG", quality=85)
    return out.getvalue()
