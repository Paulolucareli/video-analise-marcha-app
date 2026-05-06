from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile

import cv2
import numpy as np

from analysis_schema import EVENT_MARKERS


@dataclass
class LinearSummary:
    start_event: str
    end_event: str
    frame_delta: int
    time_seconds: float
    displacement_px: float
    displacement_cm: float
    displacement_m: float
    velocity_m_s: float
    direction: str


@dataclass
class LinearResults:
    summary: LinearSummary


def _ordered_event_values(markers: dict[str, str]) -> list[tuple[str, int]]:
    rows: list[tuple[str, int]] = []
    for marker in EVENT_MARKERS:
        raw_value = str(markers.get(marker["label"], "")).strip()
        if raw_value.isdigit():
            rows.append((marker["label"], int(raw_value)))
    return rows


def _candidate_foreground_boxes(frame_bgr: np.ndarray, background_bgr: np.ndarray) -> list[tuple[int, int, int, int]]:
    diff = cv2.absdiff(frame_bgr, background_bgr)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _ret, mask = cv2.threshold(gray, 24, 255, cv2.THRESH_BINARY)
    kernel = np.ones((7, 7), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return []

    height, width = gray.shape
    candidates: list[tuple[int, int, int, int]] = []
    min_area = 0.02 * width * height
    min_height = 0.34 * height
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        if h < min_height or h <= w:
            continue
        candidates.append((x, y, x + w, y + h))
    return candidates


def _select_subject_boxes(
    frames_bgr: list[np.ndarray], background_bgr: np.ndarray
) -> list[tuple[int, int, int, int]]:
    height, width = frames_bgr[0].shape[:2]
    frame_center_x = width / 2.0
    selected: list[tuple[int, int, int, int]] = []
    previous_center_x: float | None = None

    for frame_bgr in frames_bgr:
        candidates = _candidate_foreground_boxes(frame_bgr, background_bgr)
        if not candidates:
            continue

        best_box: tuple[int, int, int, int] | None = None
        best_score: float | None = None
        for x1, y1, x2, y2 in candidates:
            box_w = x2 - x1
            box_h = y2 - y1
            area = box_w * box_h
            center_x = x1 + box_w / 2.0
            center_penalty = abs(center_x - frame_center_x) / width
            continuity_penalty = 0.0 if previous_center_x is None else abs(center_x - previous_center_x) / width
            height_bonus = box_h / height
            score = (area / (width * height)) + (1.1 * height_bonus) - (1.0 * center_penalty) - (1.4 * continuity_penalty)
            if best_score is None or score > best_score:
                best_score = score
                best_box = (x1, y1, x2, y2)

        if best_box is not None:
            selected.append(best_box)
            previous_center_x = (best_box[0] + best_box[2]) / 2.0

    return selected


def compute_linear_parameters(
    video_bytes: bytes | None,
    markers: dict[str, str],
    fps: float,
    px_per_cm: float | None,
) -> LinearResults | None:
    if not video_bytes or fps <= 0 or px_per_cm is None or px_per_cm <= 0:
        return None

    ordered_events = _ordered_event_values(markers)
    if len(ordered_events) < 2:
        return None

    start_event, start_frame = ordered_events[0]
    end_event, end_frame = ordered_events[-1]
    if end_frame <= start_frame:
        return None

    sample_count = min(9, max(2, end_frame - start_frame + 1))
    sample_frames = np.linspace(start_frame, end_frame, num=sample_count, dtype=int).tolist()
    unique_frames: list[int] = []
    for frame_index in sample_frames:
        if not unique_frames or unique_frames[-1] != frame_index:
            unique_frames.append(frame_index)

    with NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        temp_file.write(video_bytes)
        temp_path = Path(temp_file.name)

    capture = cv2.VideoCapture(str(temp_path))
    if not capture.isOpened():
        capture.release()
        temp_path.unlink(missing_ok=True)
        return None

    frames_bgr: list[np.ndarray] = []
    try:
        for frame_index in unique_frames:
            capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ok, frame = capture.read()
            if ok and frame is not None:
                frames_bgr.append(frame)
    finally:
        capture.release()
        temp_path.unlink(missing_ok=True)

    if len(frames_bgr) < 2:
        return None

    background = np.median(np.stack(frames_bgr, axis=0), axis=0).astype(np.uint8)
    selected_boxes = _select_subject_boxes(frames_bgr, background)
    if len(selected_boxes) < 2:
        return None

    start_box = selected_boxes[0]
    end_box = selected_boxes[-1]
    start_center_x = (start_box[0] + start_box[2]) / 2.0
    end_center_x = (end_box[0] + end_box[2]) / 2.0
    displacement_px = abs(end_center_x - start_center_x)
    if displacement_px <= 0:
        return None

    displacement_cm = displacement_px / px_per_cm
    time_seconds = (end_frame - start_frame) / fps
    if time_seconds <= 0:
        return None

    displacement_m = displacement_cm / 100.0
    direction = "esquerda para direita" if end_center_x >= start_center_x else "direita para esquerda"
    velocity_m_s = displacement_m / time_seconds

    return LinearResults(
        summary=LinearSummary(
            start_event=start_event,
            end_event=end_event,
            frame_delta=end_frame - start_frame,
            time_seconds=round(time_seconds, 3),
            displacement_px=round(displacement_px, 2),
            displacement_cm=round(displacement_cm, 2),
            displacement_m=round(displacement_m, 3),
            velocity_m_s=round(velocity_m_s, 3),
            direction=direction,
        )
    )
