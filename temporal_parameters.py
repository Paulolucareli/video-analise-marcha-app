from __future__ import annotations

from dataclasses import dataclass, field

from analysis_schema import BILATERAL_TEMPORAL_MARKERS, EVENT_MARKERS


@dataclass
class SideSummary:
    """Resumo temporal de um único lado (direito ou esquerdo)."""
    cycle_frames: int | None = None
    cycle_seconds: float | None = None
    support_frames: int | None = None
    support_seconds: float | None = None
    support_pct: float | None = None
    swing_frames: int | None = None
    swing_seconds: float | None = None
    swing_pct: float | None = None
    first_double_support_frames: int | None = None
    first_double_support_seconds: float | None = None
    first_double_support_pct: float | None = None
    single_support_frames: int | None = None
    single_support_seconds: float | None = None
    single_support_pct: float | None = None
    second_double_support_frames: int | None = None
    second_double_support_seconds: float | None = None
    second_double_support_pct: float | None = None


@dataclass
class TemporalSummary:
    observed_cycle_frames: int | None
    observed_cycle_seconds: float | None
    support_window_frames: int | None
    support_window_seconds: float | None
    support_window_pct: float | None
    swing_window_frames: int | None
    swing_window_seconds: float | None
    swing_window_pct: float | None
    first_double_support_frames: int | None
    first_double_support_seconds: float | None
    first_double_support_pct: float | None
    single_support_frames: int | None
    single_support_seconds: float | None
    single_support_pct: float | None
    second_double_support_frames: int | None
    second_double_support_seconds: float | None
    second_double_support_pct: float | None
    right: SideSummary = field(default_factory=SideSummary)
    left: SideSummary = field(default_factory=SideSummary)
    cycle_asymmetry_pct: float | None = None


@dataclass
class TemporalResults:
    event_rows: list[dict[str, str | int | float]]
    interval_rows: list[dict[str, str | int | float]]
    side_rows: list[dict[str, str | int | float]]
    summary: TemporalSummary
    reference_pct: dict[str, float]
    source_mode: str


REFERENCE_PCT = {
    "support": 60.0,
    "swing": 40.0,
    "first_double_support": 10.0,
    "single_support": 40.0,
    "second_double_support": 10.0,
}

REFERENCE_SOURCE = "Perry & Burnfield (2010) — adulto típico, velocidade confortável"


def _seconds(frames: int, fps: float) -> float:
    return frames / fps if fps > 0 else 0.0


def _empty_summary() -> TemporalSummary:
    return TemporalSummary(
        observed_cycle_frames=None, observed_cycle_seconds=None,
        support_window_frames=None, support_window_seconds=None, support_window_pct=None,
        swing_window_frames=None, swing_window_seconds=None, swing_window_pct=None,
        first_double_support_frames=None, first_double_support_seconds=None, first_double_support_pct=None,
        single_support_frames=None, single_support_seconds=None, single_support_pct=None,
        second_double_support_frames=None, second_double_support_seconds=None, second_double_support_pct=None,
    )


def _empty_results(source_mode: str) -> TemporalResults:
    return TemporalResults(
        event_rows=[], interval_rows=[], side_rows=[],
        summary=_empty_summary(), reference_pct=REFERENCE_PCT.copy(), source_mode=source_mode,
    )


def _ordered_event_values(markers: dict[str, str]) -> list[tuple[str, int]]:
    rows: list[tuple[str, int]] = []
    for marker in EVENT_MARKERS:
        raw_value = str(markers.get(marker["label"], "")).strip()
        if raw_value.isdigit():
            rows.append((marker["label"], int(raw_value)))
    return rows


def _ordered_bilateral_values(markers: dict[str, str]) -> list[tuple[str, int]]:
    rows: list[tuple[str, int]] = []
    for marker in BILATERAL_TEMPORAL_MARKERS:
        raw_value = str(markers.get(marker["label"], "")).strip()
        if raw_value.isdigit():
            rows.append((marker["label"], int(raw_value)))
    return rows


def _validate_bilateral_order(ric1, lto1, lic1, rto1, ric2) -> bool:
    """Garante ordem cronológica correta: CI_D1 < TP_E1 < CI_E1 < TP_D1 < CI_D2."""
    return (
        ric1 is not None and lto1 is not None and lic1 is not None
        and rto1 is not None and ric2 is not None
        and ric1 < lto1 < lic1 < rto1 < ric2
    )


def _append_intervals(
    ordered_events: list[tuple[str, int]], fps: float, observed_cycle_frames: int | None,
) -> list[dict[str, str | int | float]]:
    interval_rows: list[dict[str, str | int | float]] = []
    previous_label: str | None = None
    previous_frame: int | None = None
    for label, frame_index in ordered_events:
        if previous_label is not None and previous_frame is not None and frame_index > previous_frame:
            delta_frames = frame_index - previous_frame
            pct_cycle = (
                round((delta_frames / observed_cycle_frames) * 100.0, 1)
                if observed_cycle_frames and observed_cycle_frames > 0 else None
            )
            interval_rows.append({
                "Intervalo": f"{previous_label} -> {label}",
                "Frames": delta_frames,
                "Tempo (s)": round(_seconds(delta_frames, fps), 3),
                "% do ciclo": pct_cycle if pct_cycle is not None else "-",
            })
        previous_label = label
        previous_frame = frame_index
    return interval_rows


def _build_side_row(
    side: str, cycle_frames: int | None, cycle_seconds: float | None,
    support_frames: int | None, support_seconds: float | None,
    swing_frames: int | None, swing_seconds: float | None,
    ds1_pct: float | None = None, single_support_pct: float | None = None, ds2_pct: float | None = None,
) -> dict[str, str | int | float]:
    support_pct = round((support_frames / cycle_frames) * 100.0, 1) if cycle_frames and support_frames is not None else "-"
    swing_pct = round((swing_frames / cycle_frames) * 100.0, 1) if cycle_frames and swing_frames is not None else "-"
    return {
        "Lado": side,
        "Ciclo (s)": round(cycle_seconds, 3) if cycle_seconds is not None else "-",
        "Apoio (%)": support_pct,
        "Balanço (%)": swing_pct,
        "Apoio (s)": round(support_seconds, 3) if support_seconds is not None else "-",
        "Balanço (s)": round(swing_seconds, 3) if swing_seconds is not None else "-",
        "Apoio (frames)": support_frames if support_frames is not None else "-",
        "Balanço (frames)": swing_frames if swing_frames is not None else "-",
        "1º duplo apoio (%)": ds1_pct if ds1_pct is not None else "-",
        "Apoio simples (%)": single_support_pct if single_support_pct is not None else "-",
        "2º duplo apoio (%)": ds2_pct if ds2_pct is not None else "-",
    }


def compute_temporal_parameters(
    markers: dict[str, str], fps: float, bilateral_markers: dict[str, str] | None = None,
) -> TemporalResults:
    if bilateral_markers:
        bilateral_results = compute_bilateral_temporal_parameters(bilateral_markers, fps)
        if bilateral_results.event_rows:
            return bilateral_results
    return compute_observational_temporal_parameters(markers, fps)


def compute_observational_temporal_parameters(markers: dict[str, str], fps: float) -> TemporalResults:
    ordered_events = _ordered_event_values(markers)
    if not ordered_events:
        return _empty_results("observational")

    event_rows = [
        {"Evento": label, "Frame": frame_index, "Tempo (s)": round(_seconds(frame_index, fps), 3)}
        for label, frame_index in ordered_events
    ]
    frame_map = {label: frame for label, frame in ordered_events}
    cycle_start = frame_map.get("Contato inicial")
    cycle_end = frame_map.get("Balanço terminal")
    observed_cycle_frames = cycle_end - cycle_start if cycle_start is not None and cycle_end is not None and cycle_end > cycle_start else None
    observed_cycle_seconds = _seconds(observed_cycle_frames, fps) if observed_cycle_frames is not None else None

    support_end = frame_map.get("Balanço inicial")
    support_window_frames = support_end - cycle_start if cycle_start is not None and support_end is not None and support_end > cycle_start else None
    support_window_seconds = _seconds(support_window_frames, fps) if support_window_frames is not None else None
    support_window_pct = round((support_window_frames / observed_cycle_frames) * 100.0, 1) if observed_cycle_frames and support_window_frames is not None else None

    swing_start = frame_map.get("Balanço inicial")
    swing_window_frames = cycle_end - swing_start if swing_start is not None and cycle_end is not None and cycle_end > swing_start else None
    swing_window_seconds = _seconds(swing_window_frames, fps) if swing_window_frames is not None else None
    swing_window_pct = round((swing_window_frames / observed_cycle_frames) * 100.0, 1) if observed_cycle_frames and swing_window_frames is not None else None

    return TemporalResults(
        event_rows=event_rows,
        interval_rows=_append_intervals(ordered_events, fps, observed_cycle_frames),
        side_rows=[],
        summary=TemporalSummary(
            observed_cycle_frames=observed_cycle_frames,
            observed_cycle_seconds=round(observed_cycle_seconds, 3) if observed_cycle_seconds is not None else None,
            support_window_frames=support_window_frames,
            support_window_seconds=round(support_window_seconds, 3) if support_window_seconds is not None else None,
            support_window_pct=support_window_pct,
            swing_window_frames=swing_window_frames,
            swing_window_seconds=round(swing_window_seconds, 3) if swing_window_seconds is not None else None,
            swing_window_pct=swing_window_pct,
            first_double_support_frames=None, first_double_support_seconds=None, first_double_support_pct=None,
            single_support_frames=None, single_support_seconds=None, single_support_pct=None,
            second_double_support_frames=None, second_double_support_seconds=None, second_double_support_pct=None,
        ),
        reference_pct=REFERENCE_PCT.copy(),
        source_mode="observational",
    )


def compute_bilateral_temporal_parameters(markers: dict[str, str], fps: float) -> TemporalResults:
    ordered_events = _ordered_bilateral_values(markers)
    if len(ordered_events) < 5:
        return _empty_results("bilateral")

    frame_map = {label: frame for label, frame in ordered_events}
    ric1 = frame_map.get("Contato inicial direito 1")
    lto1 = frame_map.get("Retirada do pé esquerdo 1")
    lic1 = frame_map.get("Contato inicial esquerdo 1")
    rto1 = frame_map.get("Retirada do pé direito 1")
    ric2 = frame_map.get("Contato inicial direito 2")
    lto2 = frame_map.get("Retirada do pé esquerdo 2")
    lic2 = frame_map.get("Contato inicial esquerdo 2")

    if not _validate_bilateral_order(ric1, lto1, lic1, rto1, ric2):
        return _empty_results("bilateral")

    # Ciclo DIREITO
    right_cycle_frames = ric2 - ric1
    right_cycle_seconds = _seconds(right_cycle_frames, fps)
    right_support_frames = rto1 - ric1
    right_swing_frames = ric2 - rto1
    ds1_frames = lto1 - ric1
    single_support_frames = lic1 - lto1
    ds2_frames = rto1 - lic1
    right_ds1_pct = round((ds1_frames / right_cycle_frames) * 100.0, 1)
    right_single_pct = round((single_support_frames / right_cycle_frames) * 100.0, 1)
    right_ds2_pct = round((ds2_frames / right_cycle_frames) * 100.0, 1)

    right_summary = SideSummary(
        cycle_frames=right_cycle_frames, cycle_seconds=round(right_cycle_seconds, 3),
        support_frames=right_support_frames, support_seconds=round(_seconds(right_support_frames, fps), 3),
        support_pct=round((right_support_frames / right_cycle_frames) * 100.0, 1),
        swing_frames=right_swing_frames, swing_seconds=round(_seconds(right_swing_frames, fps), 3),
        swing_pct=round((right_swing_frames / right_cycle_frames) * 100.0, 1),
        first_double_support_frames=ds1_frames, first_double_support_seconds=round(_seconds(ds1_frames, fps), 3),
        first_double_support_pct=right_ds1_pct,
        single_support_frames=single_support_frames, single_support_seconds=round(_seconds(single_support_frames, fps), 3),
        single_support_pct=right_single_pct,
        second_double_support_frames=ds2_frames, second_double_support_seconds=round(_seconds(ds2_frames, fps), 3),
        second_double_support_pct=right_ds2_pct,
    )

    side_rows = [_build_side_row(
        "Direito", right_cycle_frames, right_cycle_seconds,
        right_support_frames, _seconds(right_support_frames, fps),
        right_swing_frames, _seconds(right_swing_frames, fps),
        right_ds1_pct, right_single_pct, right_ds2_pct,
    )]

    left_summary = SideSummary()
    cycle_asymmetry_pct: float | None = None

    if None not in (lic1, lto2, lic2) and lic1 < rto1 < ric2 < lto2 < lic2:
        left_cycle_frames = lic2 - lic1
        left_cycle_seconds = _seconds(left_cycle_frames, fps)
        left_support_frames = lto2 - lic1
        left_swing_frames = lic2 - lto2
        left_ds1_frames = rto1 - lic1
        left_single_frames = ric2 - rto1
        left_ds2_frames = lto2 - ric2
        left_ds1_pct = round((left_ds1_frames / left_cycle_frames) * 100.0, 1)
        left_single_pct = round((left_single_frames / left_cycle_frames) * 100.0, 1)
        left_ds2_pct = round((left_ds2_frames / left_cycle_frames) * 100.0, 1)

        left_summary = SideSummary(
            cycle_frames=left_cycle_frames, cycle_seconds=round(left_cycle_seconds, 3),
            support_frames=left_support_frames, support_seconds=round(_seconds(left_support_frames, fps), 3),
            support_pct=round((left_support_frames / left_cycle_frames) * 100.0, 1),
            swing_frames=left_swing_frames, swing_seconds=round(_seconds(left_swing_frames, fps), 3),
            swing_pct=round((left_swing_frames / left_cycle_frames) * 100.0, 1),
            first_double_support_frames=left_ds1_frames, first_double_support_seconds=round(_seconds(left_ds1_frames, fps), 3),
            first_double_support_pct=left_ds1_pct,
            single_support_frames=left_single_frames, single_support_seconds=round(_seconds(left_single_frames, fps), 3),
            single_support_pct=left_single_pct,
            second_double_support_frames=left_ds2_frames, second_double_support_seconds=round(_seconds(left_ds2_frames, fps), 3),
            second_double_support_pct=left_ds2_pct,
        )
        side_rows.append(_build_side_row(
            "Esquerdo", left_cycle_frames, left_cycle_seconds,
            left_support_frames, _seconds(left_support_frames, fps),
            left_swing_frames, _seconds(left_swing_frames, fps),
            left_ds1_pct, left_single_pct, left_ds2_pct,
        ))
        mean_cycle = (right_cycle_seconds + left_cycle_seconds) / 2.0
        if mean_cycle > 0:
            cycle_asymmetry_pct = round(abs(right_cycle_seconds - left_cycle_seconds) / mean_cycle * 100.0, 1)

    return TemporalResults(
        event_rows=[
            {"Evento": label, "Frame": fi, "Tempo (s)": round(_seconds(fi, fps), 3)}
            for label, fi in ordered_events
        ],
        interval_rows=_append_intervals(ordered_events, fps, right_cycle_frames),
        side_rows=side_rows,
        summary=TemporalSummary(
            observed_cycle_frames=right_cycle_frames,
            observed_cycle_seconds=round(right_cycle_seconds, 3),
            support_window_frames=right_support_frames,
            support_window_seconds=round(_seconds(right_support_frames, fps), 3),
            support_window_pct=round((right_support_frames / right_cycle_frames) * 100.0, 1),
            swing_window_frames=right_swing_frames,
            swing_window_seconds=round(_seconds(right_swing_frames, fps), 3),
            swing_window_pct=round((right_swing_frames / right_cycle_frames) * 100.0, 1),
            first_double_support_frames=ds1_frames,
            first_double_support_seconds=round(_seconds(ds1_frames, fps), 3),
            first_double_support_pct=round((ds1_frames / right_cycle_frames) * 100.0, 1),
            single_support_frames=single_support_frames,
            single_support_seconds=round(_seconds(single_support_frames, fps), 3),
            single_support_pct=round((single_support_frames / right_cycle_frames) * 100.0, 1),
            second_double_support_frames=ds2_frames,
            second_double_support_seconds=round(_seconds(ds2_frames, fps), 3),
            second_double_support_pct=round((ds2_frames / right_cycle_frames) * 100.0, 1),
            right=right_summary,
            left=left_summary,
            cycle_asymmetry_pct=cycle_asymmetry_pct,
        ),
        reference_pct=REFERENCE_PCT.copy(),
        source_mode="bilateral",
    )
