"""Gerador do infográfico temporal de marcha.

Melhorias v2:
- Fontes cross-platform: tenta várias paths (macOS, Linux, Docker) antes de fallback
- Layout redesenhado: 3 linhas por variável (Direito / Esquerdo / Referência) lado a lado
- Coluna de assimetria (Δ) explícita
- Rodapé com fonte da referência
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from linear_parameters import LinearResults
from temporal_parameters import TemporalResults


# --- Paleta ---
BG     = (246, 247, 251)
PANEL  = (255, 255, 255)
INK    = (28,  38,  50)
MUTED  = (96,  108, 122)
GRID   = (221, 226, 236)
RIGHT  = (24,  95,  165)   # azul — lado direito
LEFT   = (15,  110, 86)    # verde — lado esquerdo
REF    = (180, 56,  67)    # vermelho — referência
OK     = (47,  137, 92)
WARN   = (219, 142, 27)
ALERT  = (196, 62,  62)
ACCENT = (33,  106, 168)


# --- Fontes cross-platform ---
_FONT_CACHE: dict[tuple[int, bool], ImageFont.ImageFont] = {}

def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    key = (size, bold)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]

    candidates = []
    if bold:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",   # macOS
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", # Ubuntu/Docker
            "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]

    for path in candidates:
        try:
            font = ImageFont.truetype(path, size=size)
            _FONT_CACHE[key] = font
            return font
        except (OSError, IOError):
            continue

    # Fallback: usa fonte bitmap padrão (visível mas pequena)
    font = ImageFont.load_default()
    _FONT_CACHE[key] = font
    return font


def _severity_color(delta: float | None, thresholds: tuple[float, float] = (3.0, 7.0)) -> tuple[int, int, int]:
    if delta is None:
        return ACCENT
    if delta <= thresholds[0]:
        return OK
    if delta <= thresholds[1]:
        return WARN
    return ALERT


def _draw_card(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    value: str,
    subtitle: str,
    color: tuple[int, int, int],
) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=18, fill=PANEL, outline=GRID, width=2)
    draw.rounded_rectangle((x1 + 16, y1 + 16, x1 + 28, y1 + 48), radius=6, fill=color)
    draw.text((x1 + 42, y1 + 14), title, fill=MUTED, font=_font(17))
    draw.text((x1 + 18, y1 + 54), value, fill=INK, font=_font(26, bold=True))
    draw.text((x1 + 18, y1 + 90), subtitle, fill=MUTED, font=_font(14))


def _draw_bilateral_bar(
    draw: ImageDraw.ImageDraw,
    label: str,
    right_pct: float | None,
    left_pct: float | None,
    ref_pct: float,
    top: int,
    bar_left: int,
    bar_right: int,
    row_height: int = 72,
) -> None:
    """Desenha três barras horizontais sobrepostas (direita, esquerda, referência)."""
    width = bar_right - bar_left

    # Label da variável
    draw.text((bar_left - 190, top + row_height // 2 - 8), label, fill=INK, font=_font(17, bold=True))

    def bar_y(row: int) -> tuple[int, int]:
        h = 18
        spacing = 22
        y0 = top + row * spacing
        return y0, y0 + h

    # Fundo cinza
    y0, y1 = bar_y(0)
    draw.rounded_rectangle((bar_left, top, bar_right, top + row_height - 6), radius=10, fill=(240, 241, 246))

    # Referência (linha vertical vermelha)
    ref_x = int(bar_left + (ref_pct / 100.0) * width)
    draw.line((ref_x, top - 4, ref_x, top + row_height + 4), fill=REF, width=3)
    draw.text((ref_x - 22, top - 20), f"ref {ref_pct:.0f}%", fill=REF, font=_font(13, bold=True))

    # Barra direito
    if right_pct is not None:
        rx = int(bar_left + (min(right_pct, 100) / 100.0) * width)
        color = _severity_color(abs(right_pct - ref_pct))
        y0r, y1r = bar_y(0)
        draw.rounded_rectangle((bar_left, y0r + top, rx, y1r + top), radius=8, fill=(*color, 200))
        draw.text((rx + 6, y0r + top), f"D {right_pct:.1f}%", fill=color, font=_font(14, bold=True))
    else:
        y0r, y1r = bar_y(0)
        draw.text((bar_left + 4, y0r + top), "D —", fill=MUTED, font=_font(14))

    # Barra esquerdo
    if left_pct is not None:
        lx = int(bar_left + (min(left_pct, 100) / 100.0) * width)
        color_l = _severity_color(abs(left_pct - ref_pct))
        y0l, y1l = bar_y(1)
        draw.rounded_rectangle((bar_left, y0l + top, lx, y1l + top), radius=8, fill=(*color_l, 160))
        draw.text((lx + 6, y0l + top), f"E {left_pct:.1f}%", fill=color_l, font=_font(14, bold=True))
    else:
        y0l, y1l = bar_y(1)
        draw.text((bar_left + 4, y0l + top), "E —", fill=MUTED, font=_font(14))

    # Delta
    if right_pct is not None and left_pct is not None:
        delta = abs(right_pct - left_pct)
        delta_color = _severity_color(delta)
        draw.text((bar_right + 12, top + row_height // 2 - 10), f"Δ {delta:.1f}%", fill=delta_color, font=_font(15, bold=True))


def _value_from_side_row(row: dict[str, str | int | float], key: str) -> float | None:
    value = row.get(key)
    if isinstance(value, (int, float)):
        return float(value)
    return None


def build_temporal_infographic(
    temporal_results: TemporalResults | None,
    linear_results: LinearResults | None = None,
) -> bytes | None:
    if temporal_results is None or temporal_results.summary.observed_cycle_frames is None:
        return None

    width = 1640
    height = 1060
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((24, 24, width - 24, height - 24), radius=30, fill=(250, 251, 255))

    # Cabeçalho
    draw.text((72, 60), "Painel comparativo do ciclo de marcha", fill=INK, font=_font(32, bold=True))
    draw.text((72, 102), "Direito vs. esquerdo com referência temporal clínica", fill=MUTED, font=_font(18))

    summary = temporal_results.summary
    right_row = next((r for r in temporal_results.side_rows if r.get("Lado") == "Direito"), None)
    left_row  = next((r for r in temporal_results.side_rows if r.get("Lado") == "Esquerdo"), None)

    right_cycle_s = _value_from_side_row(right_row, "Ciclo (s)") if right_row else None
    left_cycle_s  = _value_from_side_row(left_row, "Ciclo (s)") if left_row else None
    asym = summary.cycle_asymmetry_pct

    # Cards de resumo topo
    card_h = 132
    card_gap = 16
    n_cards = 4
    card_w = int((width - 144 - (n_cards - 1) * card_gap) / n_cards)
    card_top = 146

    def bilateral_pct_text(metric: str) -> str:
        rv = _value_from_side_row(right_row, metric) if right_row else None
        lv = _value_from_side_row(left_row, metric) if left_row else None
        rt = f"D {rv:.1f}%" if rv is not None else "D —"
        lt = f"E {lv:.1f}%" if lv is not None else "E —"
        return f"{rt}  |  {lt}"

    cycle_val = "D —  |  E —"
    if right_cycle_s is not None or left_cycle_s is not None:
        rt = f"D {right_cycle_s:.3f}s" if right_cycle_s is not None else "D —"
        lt = f"E {left_cycle_s:.3f}s" if left_cycle_s is not None else "E —"
        cycle_val = f"{rt}  |  {lt}"

    cards = [
        ("Ciclo de marcha", cycle_val, f"assimetria {asym:.1f}%" if asym is not None else "assimetria —", _severity_color(asym)),
        ("1º duplo apoio", bilateral_pct_text("1º duplo apoio (%)"), f"ref. {temporal_results.reference_pct['first_double_support']:.0f}% por lado", ACCENT),
        ("Apoio simples", bilateral_pct_text("Apoio simples (%)"), f"ref. {temporal_results.reference_pct['single_support']:.0f}% por lado", LEFT),
        ("2º duplo apoio", bilateral_pct_text("2º duplo apoio (%)"), f"ref. {temporal_results.reference_pct['second_double_support']:.0f}% por lado", ACCENT),
    ]
    for idx, (title, value, subtitle, color) in enumerate(cards):
        x1 = 72 + idx * (card_w + card_gap)
        _draw_card(draw, (x1, card_top, x1 + card_w, card_top + card_h), title, value, subtitle, color)

    # Painel de barras bilaterais
    panel_top = 310
    panel_bottom = height - 100
    draw.rounded_rectangle((72, panel_top, width - 72, panel_bottom), radius=24, fill=PANEL, outline=GRID, width=2)

    draw.text((102, panel_top + 18), "Distribuição das fases do ciclo", fill=INK, font=_font(22, bold=True))
    draw.text((102, panel_top + 48), "Linha vermelha = referência clínica · verde = próximo · amarelo = desvio moderado · vermelho = desvio importante", fill=MUTED, font=_font(15))

    bar_left  = 292
    bar_right = width - 160
    row_h = 72
    row_gap = 12

    variables = [
        ("Apoio", "Apoio (%)", temporal_results.reference_pct["support"]),
        ("Balanço", "Balanço (%)", temporal_results.reference_pct["swing"]),
        ("1º duplo apoio", "1º duplo apoio (%)", temporal_results.reference_pct["first_double_support"]),
        ("Apoio simples", "Apoio simples (%)", temporal_results.reference_pct["single_support"]),
        ("2º duplo apoio", "2º duplo apoio (%)", temporal_results.reference_pct["second_double_support"]),
    ]

    current_y = panel_top + 90
    for var_label, metric_key, ref_pct in variables:
        right_pct = _value_from_side_row(right_row, metric_key) if right_row else None
        left_pct  = _value_from_side_row(left_row, metric_key) if left_row else None
        _draw_bilateral_bar(draw, var_label, right_pct, left_pct, ref_pct, current_y, bar_left, bar_right, row_h)

        # Separador
        if var_label != "2º duplo apoio":
            draw.line((bar_left - 190, current_y + row_h + row_gap // 2, bar_right + 80, current_y + row_h + row_gap // 2),
                      fill=GRID, width=1)
        current_y += row_h + row_gap

    # Legenda
    leg_y = panel_bottom + 16
    for color, label in [(RIGHT, "Lado direito"), (LEFT, "Lado esquerdo"), (REF, "Referência clínica"), (OK, "Dentro do esperado"), (WARN, "Desvio moderado"), (ALERT, "Desvio importante")]:
        draw.rounded_rectangle((bar_left, leg_y + 4, bar_left + 14, leg_y + 18), radius=3, fill=color)
        draw.text((bar_left + 20, leg_y), label, fill=MUTED, font=_font(14))
        bar_left += 160

    # Rodapé com referência
    draw.text((72, height - 44), f"Referência: Perry & Burnfield (2010) — Gait Analysis: Normal and Pathological Function. Adulto típico, velocidade confortável.", fill=MUTED, font=_font(13))

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
