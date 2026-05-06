from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

import cv2
import numpy as np
from PIL import Image, ImageDraw


@dataclass
class DetectedSegment:
    x1: int
    y1: int
    x2: int
    y2: int
    length_px: float


@dataclass
class CalibrationResult:
    image_size: tuple[int, int]
    horizontal_segment: DetectedSegment | None
    oblique_segment: DetectedSegment | None
    preview_bytes: bytes | None


def _detect_segments(image_bgr: np.ndarray) -> tuple[DetectedSegment | None, DetectedSegment | None]:
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    mask = cv2.inRange(gray, 0, 55)
    lines = cv2.HoughLinesP(mask, 1, np.pi / 180, threshold=10, minLineLength=35, maxLineGap=35)
    if lines is None:
        return None, None

    horizontal_candidates: list[DetectedSegment] = []
    oblique_candidates: list[DetectedSegment] = []

    for raw in lines[:, 0, :]:
        x1, y1, x2, y2 = map(int, raw)
        length_px = float(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
        angle = float(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
        segment = DetectedSegment(x1=x1, y1=y1, x2=x2, y2=y2, length_px=length_px)
        if abs(angle) < 12:
            horizontal_candidates.append(segment)
        elif -70 < angle < -20:
            oblique_candidates.append(segment)

    horizontal_segment = max(horizontal_candidates, key=lambda seg: seg.length_px, default=None)
    oblique_segment = max(oblique_candidates, key=lambda seg: seg.length_px, default=None)
    return horizontal_segment, oblique_segment


def _build_preview(image_rgb: np.ndarray, horizontal: DetectedSegment | None, oblique: DetectedSegment | None) -> bytes:
    image = Image.fromarray(image_rgb.copy())
    draw = ImageDraw.Draw(image)
    if horizontal is not None:
        draw.line((horizontal.x1, horizontal.y1, horizontal.x2, horizontal.y2), fill=(0, 180, 0), width=8)
    if oblique is not None:
        draw.line((oblique.x1, oblique.y1, oblique.x2, oblique.y2), fill=(220, 0, 0), width=8)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def build_calibration_preview(
    image_bytes: bytes,
    horizontal: DetectedSegment | None,
    oblique: DetectedSegment | None,
) -> bytes:
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    rgb = np.array(image)
    return _build_preview(rgb, horizontal, oblique)


def analyze_calibration_image(image_bytes: bytes) -> CalibrationResult:
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    rgb = np.array(image)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    horizontal, oblique = _detect_segments(bgr)
    preview = _build_preview(rgb, horizontal, oblique)
    return CalibrationResult(
        image_size=(image.width, image.height),
        horizontal_segment=horizontal,
        oblique_segment=oblique,
        preview_bytes=preview,
    )
