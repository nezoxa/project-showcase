"""Build the final verdict from a count and an optional target quantity."""

from dataclasses import dataclass
from enum import Enum


class CountStatus(str, Enum):
    COUNTED = "counted"
    MATCH = "match"
    SHORTAGE = "shortage"
    EXCESS = "excess"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class CountResult:
    detected: int
    expected: int | None
    status: CountStatus
    note: str


def build_count_result(
    detected: int,
    *,
    expected_count: int | None,
    needs_review: bool = False,
) -> CountResult:
    if detected == 0 and expected_count:
        status = CountStatus.REVIEW_REQUIRED
        note = "объекты не обнаружены — проверьте фото (свет/ракурс/резкость)"
    elif needs_review and detected > 0:
        status = CountStatus.REVIEW_REQUIRED
        note = "не удалось надёжно посчитать — нужна ручная проверка"
    elif expected_count is None:
        status = CountStatus.COUNTED
        note = f"объектов на фото: {detected}"
    elif detected == expected_count:
        status = CountStatus.MATCH
        note = "количество совпадает"
    elif detected < expected_count:
        status = CountStatus.SHORTAGE
        note = f"не хватает: {expected_count - detected}"
    else:
        status = CountStatus.EXCESS
        note = f"лишних: {detected - expected_count}"

    return CountResult(detected=detected, expected=expected_count, status=status, note=note)
