from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps


@dataclass
class FrameSnapshot:
    label: str
    frame_index: int
    image_bytes: bytes


@dataclass
class FrameExportAssets:
    snapshots: list[FrameSnapshot]
    montage_bytes: bytes | None


@dataclass
class VideoMetadata:
    fps: float | None
    total_frames: int | None


def detect_video_fps(video_bytes: bytes) -> float | None:
    if not video_bytes:
        return None

    with NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        temp_file.write(video_bytes)
        temp_path = Path(temp_file.name)

    capture = cv2.VideoCapture(str(temp_path))
    try:
        if not capture.isOpened():
            return None
        fps = float(capture.get(cv2.CAP_PROP_FPS) or 0.0)
        if fps <= 0:
            return None
        return fps
    finally:
        capture.release()
        temp_path.unlink(missing_ok=True)


def read_video_metadata(video_bytes: bytes) -> VideoMetadata:
    if not video_bytes:
        return VideoMetadata(fps=None, total_frames=None)

    with NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        temp_file.write(video_bytes)
        temp_path = Path(temp_file.name)

    capture = cv2.VideoCapture(str(temp_path))
    try:
        if not capture.isOpened():
            return VideoMetadata(fps=None, total_frames=None)
        fps = float(capture.get(cv2.CAP_PROP_FPS) or 0.0)
        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        return VideoMetadata(
            fps=fps if fps > 0 else None,
            total_frames=total_frames if total_frames > 0 else None,
        )
    finally:
        capture.release()
        temp_path.unlink(missing_ok=True)


def _encode_png(frame_rgb: np.ndarray) -> bytes:
    image = Image.fromarray(frame_rgb)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


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


def _compute_consistent_crop(frames_bgr: list[np.ndarray]) -> tuple[int, int, int, int]:
    height, width = frames_bgr[0].shape[:2]
    background = np.median(np.stack(frames_bgr, axis=0), axis=0).astype(np.uint8)
    boxes = _select_subject_boxes(frames_bgr, background)

    if not boxes:
        return 0, 0, width, height

    lefts = np.array([box[0] for box in boxes], dtype=np.float32)
    tops = np.array([box[1] for box in boxes], dtype=np.float32)
    rights = np.array([box[2] for box in boxes], dtype=np.float32)
    bottoms = np.array([box[3] for box in boxes], dtype=np.float32)

    x1 = int(np.percentile(lefts, 15))
    y1 = int(np.percentile(tops, 10))
    x2 = int(np.percentile(rights, 85))
    y2 = int(np.percentile(bottoms, 90))

    box_w = x2 - x1
    box_h = y2 - y1
    x_pad = int(box_w * 0.08)
    y_pad_top = int(box_h * 0.12)
    y_pad_bottom = int(box_h * 0.06)

    x1 = max(0, x1 - x_pad)
    x2 = min(width, x2 + x_pad)
    y1 = max(0, y1 - y_pad_top)
    y2 = min(height, y2 + y_pad_bottom)

    crop_w = x2 - x1
    crop_h = y2 - y1
    min_ratio = 0.36
    target_w = max(crop_w, int(crop_h * min_ratio))
    if target_w > crop_w:
        extra = target_w - crop_w
        x1 = max(0, x1 - extra // 2)
        x2 = min(width, x2 + (extra - extra // 2))

    min_height = int(height * 0.62)
    if crop_h < min_height:
        extra_h = min_height - crop_h
        y1 = max(0, y1 - int(extra_h * 0.55))
        y2 = min(height, y2 + int(extra_h * 0.45))

    return x1, y1, x2, y2


def _build_montage(snapshots: list[FrameSnapshot]) -> bytes | None:
    if not snapshots:
        return None

    support_labels = {
        "Contato inicial",
        "Resposta à carga",
        "Médio apoio",
        "Apoio terminal",
        "Pré-balanço",
    }
    support = [snapshot for snapshot in snapshots if snapshot.label in support_labels]
    swing = [snapshot for snapshot in snapshots if snapshot.label not in support_labels]

    target_height = 360
    gap = 14
    side_padding = 18
    top_padding = 18
    section_gap = 30
    label_band = 34

    def resize_group(group: list[FrameSnapshot]) -> tuple[list[Image.Image], int]:
        resized: list[Image.Image] = []
        total_width = 0
        for snapshot in group:
            image = Image.open(BytesIO(snapshot.image_bytes)).convert("RGB")
            image = ImageOps.contain(image, (9999, target_height))
            ratio = target_height / image.height
            target_width = max(1, int(image.width * ratio))
            resized_image = image.resize((target_width, target_height))
            resized.append(resized_image)
            total_width += target_width
        if resized:
            total_width += gap * (len(resized) - 1)
        return resized, total_width

    support_images, support_width = resize_group(support)
    swing_images, swing_width = resize_group(swing)
    canvas_width = max(support_width, swing_width) + (side_padding * 2)
    canvas_height = top_padding + label_band + target_height
    if swing_images:
        canvas_height += section_gap + label_band + target_height
    canvas_height += top_padding
    canvas = Image.new("RGB", (canvas_width, canvas_height), color=(255, 255, 255))

    def paste_group(images: list[Image.Image], y: int) -> int:
        if not images:
            return y
        cursor_x = side_padding + int((canvas_width - (side_padding * 2) - sum(image.width for image in images) - gap * (len(images) - 1)) / 2)
        for image in images:
            canvas.paste(image, (cursor_x, y))
            cursor_x += image.width + gap
        return y + target_height

    draw = ImageDraw.Draw(canvas)
    current_y = top_padding
    draw.text((side_padding, current_y), "Fase de apoio", fill=(32, 44, 58))
    current_y += label_band
    current_y = paste_group(support_images, current_y)

    if swing_images:
        current_y += section_gap
        draw.text((side_padding, current_y), "Fase de balanço", fill=(32, 44, 58))
        current_y += label_band
        paste_group(swing_images, current_y)

    buffer = BytesIO()
    canvas.save(buffer, format="PNG")
    return buffer.getvalue()


def extract_single_frame(video_bytes: bytes, frame_index: int) -> bytes | None:
    if not video_bytes:
        return None

    with NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        temp_file.write(video_bytes)
        temp_path = Path(temp_file.name)

    capture = cv2.VideoCapture(str(temp_path))
    try:
        if not capture.isOpened():
            return None
        capture.set(cv2.CAP_PROP_POS_FRAMES, max(0, frame_index))
        ok, frame = capture.read()
        if not ok or frame is None:
            return None
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return _encode_png(frame_rgb)
    finally:
        capture.release()
        temp_path.unlink(missing_ok=True)


def extract_frame_export_assets(video_bytes: bytes, markers: dict[str, str]) -> FrameExportAssets:
    if not video_bytes:
        return FrameExportAssets(snapshots=[], montage_bytes=None)

    ordered_markers = [(label, str(value).strip()) for label, value in markers.items() if str(value).strip().isdigit()]
    if not ordered_markers:
        return FrameExportAssets(snapshots=[], montage_bytes=None)

    with NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        temp_file.write(video_bytes)
        temp_path = Path(temp_file.name)

    capture = cv2.VideoCapture(str(temp_path))
    if not capture.isOpened():
        capture.release()
        temp_path.unlink(missing_ok=True)
        return FrameExportAssets(snapshots=[], montage_bytes=None)

    raw_frames: list[tuple[str, int, np.ndarray]] = []
    try:
        for label, value in ordered_markers:
            frame_index = max(0, int(value))
            capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ok, frame = capture.read()
            if ok and frame is not None:
                raw_frames.append((label, frame_index, frame))
    finally:
        capture.release()
        temp_path.unlink(missing_ok=True)

    if not raw_frames:
        return FrameExportAssets(snapshots=[], montage_bytes=None)

    crop_box = _compute_consistent_crop([frame for _, _, frame in raw_frames])
    x1, y1, x2, y2 = crop_box

    snapshots: list[FrameSnapshot] = []
    for label, frame_index, frame_bgr in raw_frames:
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        cropped = frame_rgb[y1:y2, x1:x2]
        snapshots.append(
            FrameSnapshot(
                label=label,
                frame_index=frame_index,
                image_bytes=_encode_png(cropped),
            )
        )

    return FrameExportAssets(
        snapshots=snapshots,
        montage_bytes=_build_montage(snapshots),
    )
