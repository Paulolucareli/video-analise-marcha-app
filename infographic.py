"""
Infográfico temporal de marcha — v5
Dot-plot comparativo com matplotlib. Sem coordenadas manuais, sem overlap.
"""
from __future__ import annotations

from io import BytesIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

from linear_parameters import LinearResults
from temporal_parameters import TemporalResults

# Paleta
C_RIGHT = "#1A5FAB"
C_LEFT  = "#0E7256"
C_REF   = "#C0392B"
C_BG    = "#FAFBFD"
C_BAND  = "#F0F3F8"
C_INK   = "#1C2632"
C_MUTED = "#5C6878"
C_GRID  = "#DDE2EC"
C_OK    = "#2E8B57"
C_WARN  = "#D4860F"
C_ALERT = "#B03030"


def _severity(delta: float) -> str:
    if delta <= 3.0:  return C_OK
    if delta <= 7.0:  return C_WARN
    return C_ALERT


def _val(row: dict | None, key: str) -> float | None:
    if row is None:
        return None
    v = row.get(key)
    return float(v) if isinstance(v, (int, float)) else None


def _card_text(rrow, lrow, key):
    rv = _val(rrow, key)
    lv = _val(lrow, key)
    rv_s = f"D {rv:.1f}%" if rv is not None else "D —"
    lv_s = f"E {lv:.1f}%" if lv is not None else "E —"
    return f"{rv_s}   {lv_s}"


def build_temporal_infographic(
    temporal_results: TemporalResults | None,
    linear_results: LinearResults | None = None,
) -> bytes | None:
    if temporal_results is None or temporal_results.summary.observed_cycle_frames is None:
        return None

    s    = temporal_results.summary
    rrow = next((r for r in temporal_results.side_rows if r.get("Lado") == "Direito"), None)
    lrow = next((r for r in temporal_results.side_rows if r.get("Lado") == "Esquerdo"), None)
    ref  = temporal_results.reference_pct

    variables = [
        ("Apoio",          "Apoio (%)",         ref["support"]),
        ("Balanço",        "Balanço (%)",        ref["swing"]),
        ("1º duplo apoio", "1º duplo apoio (%)", ref["first_double_support"]),
        ("Apoio simples",  "Apoio simples (%)",  ref["single_support"]),
        ("2º duplo apoio", "2º duplo apoio (%)", ref["second_double_support"]),
    ]

    labels = [v[0] for v in variables]
    refs   = [v[2] for v in variables]
    rights = [_val(rrow, v[1]) for v in variables]
    lefts  = [_val(lrow, v[1]) for v in variables]
    n      = len(variables)
    y_pos  = list(range(n - 1, -1, -1))

    # ── Figura: cards em cima + dot-plot embaixo ──────────────────────────────
    fig = plt.figure(figsize=(14, 10), facecolor=C_BG)
    gs  = fig.add_gridspec(2, 4,
                           height_ratios=[1, 3],
                           left=0.04, right=0.96,
                           top=0.90, bottom=0.08,
                           hspace=0.45, wspace=0.25)

    # ── Cards de métricas ─────────────────────────────────────────────────────
    rc   = _val(rrow, "Ciclo (s)")
    lc   = _val(lrow, "Ciclo (s)")
    asym = s.cycle_asymmetry_pct

    cyc_val = (f"D {rc:.3f}s   E {lc:.3f}s" if rc and lc else
               f"D {rc:.3f}s" if rc else f"E {lc:.3f}s" if lc else "—")

    card_data = [
        ("Ciclo de marcha",
         cyc_val,
         f"assimetria {asym:.1f}%" if asym is not None else "assimetria —",
         _severity(asym) if asym is not None else C_MUTED),
        ("1º duplo apoio",
         _card_text(rrow, lrow, "1º duplo apoio (%)"),
         f"referência {ref['first_double_support']:.0f}% por lado",
         C_RIGHT),
        ("Apoio simples",
         _card_text(rrow, lrow, "Apoio simples (%)"),
         f"referência {ref['single_support']:.0f}% por lado",
         C_LEFT),
        ("2º duplo apoio",
         _card_text(rrow, lrow, "2º duplo apoio (%)"),
         f"referência {ref['second_double_support']:.0f}% por lado",
         C_RIGHT),
    ]

    for col, (title, value, sub, accent) in enumerate(card_data):
        ax_c = fig.add_subplot(gs[0, col])
        ax_c.set_facecolor("white")
        for spine in ax_c.spines.values():
            spine.set_edgecolor(C_GRID)
            spine.set_linewidth(1.2)
        ax_c.set_xticks([]); ax_c.set_yticks([])

        ax_c.add_patch(mpatches.FancyBboxPatch(
            (0, 0.80), 1, 0.20,
            boxstyle="square,pad=0",
            transform=ax_c.transAxes,
            facecolor=accent, alpha=0.15,
            clip_on=False, zorder=0
        ))
        ax_c.text(0.5, 0.90, title,
                  transform=ax_c.transAxes, ha="center", va="center",
                  fontsize=10, color=C_INK, fontweight="bold")
        ax_c.text(0.5, 0.52, value,
                  transform=ax_c.transAxes, ha="center", va="center",
                  fontsize=11, color=C_INK, fontweight="bold")
        ax_c.text(0.5, 0.15, sub,
                  transform=ax_c.transAxes, ha="center", va="center",
                  fontsize=9, color=C_MUTED)

    # ── Dot-plot ──────────────────────────────────────────────────────────────
    ax = fig.add_subplot(gs[1, :])
    ax.set_facecolor(C_BG)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Faixas zebradas
    for i, yi in enumerate(y_pos):
        ax.axhspan(yi - 0.45, yi + 0.45,
                   color=C_BAND if i % 2 == 0 else "white", zorder=0)

    # Grade vertical
    ax.xaxis.grid(True, color=C_GRID, linewidth=0.8, linestyle="--", zorder=1)
    ax.set_axisbelow(True)

    for yi, ref_v, rv, lv in zip(y_pos, refs, rights, lefts):

        # Faixa de normalidade ± 5%
        ax.barh(yi, 10, left=ref_v - 5, height=0.65,
                color=C_REF, alpha=0.07, zorder=2)

        # Linha de referência
        ax.axvline(ref_v, color=C_REF, linewidth=1.2,
                   linestyle="--", alpha=0.55, zorder=2)
        ax.text(ref_v, n - 0.15,
                f"{ref_v:.0f}%",
                ha="center", va="bottom",
                fontsize=8, color=C_REF)

        # Linha conectando D–E
        if rv is not None and lv is not None:
            ax.plot([rv, lv], [yi, yi],
                    color="#CCCCCC", linewidth=2.5,
                    zorder=3, solid_capstyle="round")

        # Dot direito ●
        if rv is not None:
            ax.scatter(rv, yi, s=200, color=C_RIGHT, zorder=5, linewidths=0)
            ax.text(rv, yi + 0.28,
                    f"D {rv:.1f}%",
                    ha="center", va="bottom",
                    fontsize=9.5, color=C_RIGHT, fontweight="bold")

        # Dot esquerdo ◆
        if lv is not None:
            ax.scatter(lv, yi, s=160, color=C_LEFT,
                       zorder=5, marker="D", linewidths=0)
            ax.text(lv, yi - 0.28,
                    f"E {lv:.1f}%",
                    ha="center", va="top",
                    fontsize=9.5, color=C_LEFT, fontweight="bold")

        # Delta à direita (coordenadas absolutas — sem transform)
        if rv is not None and lv is not None:
            delta = abs(rv - lv)
            dc = _severity(delta)
            ax.text(102, yi,
                    f"Δ {delta:.1f}%",
                    va="center", ha="left",
                    fontsize=9.5, color=dc, fontweight="bold",
                    clip_on=False)

    # Eixos
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=12, color=C_INK, fontweight="bold")
    ax.tick_params(axis="y", length=0, pad=12)
    ax.tick_params(axis="x", labelsize=9, colors=C_MUTED)
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.65, n - 0.35)
    ax.set_xlabel("% do ciclo de marcha",
                  fontsize=10, color=C_MUTED, labelpad=8)

    # Legenda
    legend_elements = [
        Line2D([0], [0], marker="o", color="w",
               markerfacecolor=C_RIGHT, markersize=11, label="Lado direito"),
        Line2D([0], [0], marker="D", color="w",
               markerfacecolor=C_LEFT, markersize=10, label="Lado esquerdo"),
        Line2D([0], [0], color=C_REF, linewidth=1.5,
               linestyle="--", label="Referência clínica"),
        mpatches.Patch(facecolor=C_OK,   label="Desvio ≤ 3%"),
        mpatches.Patch(facecolor=C_WARN, label="Desvio 3–7%"),
        mpatches.Patch(facecolor=C_ALERT, label="Desvio > 7%"),
    ]
    ax.legend(handles=legend_elements,
              loc="lower right", fontsize=9,
              framealpha=0.95, edgecolor=C_GRID, ncol=3)

    # Títulos
    fig.suptitle("Painel comparativo do ciclo de marcha",
                 fontsize=16, fontweight="bold",
                 color=C_INK, x=0.04, ha="left", y=0.97)
    fig.text(0.04, 0.93,
             "Direito vs. esquerdo com referência temporal clínica  ·  "
             "Perry & Burnfield (2010)",
             fontsize=9.5, color=C_MUTED)

    buf = BytesIO()
    fig.savefig(buf, format="PNG", dpi=150,
                bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    return buf.getvalue()
