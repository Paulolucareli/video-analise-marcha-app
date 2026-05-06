"""Utilitários de visão computacional compartilhados entre frame_export e linear_parameters.

Este módulo elimina a duplicação de _candidate_foreground_boxes e _select_subject_boxes
que existia nos dois módulos originais.
"""
from __future__ import annotations

import cv2
import numpy as np


def candidate_foreground_boxes(
    frame_bgr: np.ndarray, background_bgr: np.ndarray
) -> list[tuple[int, int, int, int]]:
    """Retorna bounding boxes de candidatos a foreground via background subtraction."""
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


def select_subject_boxes(
    frames_bgr: list[np.ndarray], background_bgr: np.ndarray
) -> list[tuple[int, int, int, int]]:
    """Seleciona o bounding box do sujeito principal em cada frame."""
    height, width = frames_bgr[0].shape[:2]
    frame_center_x = width / 2.0
    selected: list[tuple[int, int, int, int]] = []
    previous_center_x: float | None = None

    for frame_bgr in frames_bgr:
        candidates = candidate_foreground_boxes(frame_bgr, background_bgr)
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
