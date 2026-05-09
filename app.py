from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

CURRENT_DIR = Path(__file__).resolve().parent
VENDOR_DIR = CURRENT_DIR / ".vendor"
if str(VENDOR_DIR) not in sys.path:
    sys.path.insert(0, str(VENDOR_DIR))

from analysis_schema import (  # noqa: E402
    FOOT_CLEARANCE_OPTIONS,
    FOOT_PROGRESSION_OPTIONS,
    FOREFOOT_OPTIONS,
    GAIT_MODE_OPTIONS,
    HEEL_OFF_OPTIONS,
    HIP_ADDUCTION_OPTIONS,
    HIP_EXTENSION_OPTIONS,
    HIP_FLEXION_OPTIONS,
    HIP_ROTATION_OPTIONS,
    HIP_SWING_FRONTAL_OPTIONS,
    HIP_SWING_OPTIONS,
    INITIAL_CONTACT_OPTIONS,
    KNEE_EXTENSION_OPTIONS,
    KNEE_FLEXION_OPTIONS,
    KNEE_TERMINAL_OPTIONS,
    LEG_ADVANCEMENT_OPTIONS,
    LOADING_RESPONSE_OPTIONS,
    MIDSTANCE_OPTIONS,
    PELVIS_OBLIQUITY_OPTIONS,
    PELVIS_ROTATION_OPTIONS,
    PELVIS_TILT_OPTIONS,
    PLANTAR_FLEXION_OPTIONS,
    RETROFOOT_OPTIONS,
    ROLLING_OPTIONS,
    STEP_WIDTH_OPTIONS,
    SUPPORT_OPTIONS,
    SWING_PROGRESSION_OPTIONS,
    TRUNK_LEAN_OPTIONS,
    TRUNK_POSITION_OPTIONS,
    UPPER_LIMB_OPTIONS,
    EVENT_MARKERS,
    BILATERAL_TEMPORAL_MARKERS,
)
from calibration import DetectedSegment, analyze_calibration_image, build_calibration_preview  # noqa: E402
from frame_export import (  # noqa: E402
    detect_video_fps,
    extract_frame_export_assets,
    extract_single_frame,
    read_video_metadata,
)
from infographic import build_temporal_infographic  # noqa: E402
from narrative import ReportData, build_docx_bytes, build_report_text, compact_lines  # noqa: E402
from temporal_parameters import compute_temporal_parameters  # noqa: E402


st.set_page_config(page_title="Analise de Video da Marcha", layout="wide")


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .left-sticky {
            position: sticky;
            top: 1rem;
        }
        .video-shell {
            margin: 0 0 1rem 0;
        }
        .section-card {
            border: 1px solid rgba(49, 51, 63, 0.18);
            border-radius: 16px;
            padding: 1rem 1rem 0.5rem 1rem;
            margin-bottom: 1rem;
            background: rgba(250, 250, 252, 0.88);
        }
        .center-block {
            max-width: 1280px;
            margin: 0 auto;
        }
        .video-caption {
            font-size: 0.92rem;
            color: #5c6470;
            margin-top: 0.35rem;
            margin-bottom: 0.75rem;
        }
        .right-note {
            font-size: 0.9rem;
            color: #5c6470;
            margin-bottom: 0.75rem;
        }
        .mini-note {
            font-size: 0.9rem;
            color: #5c6470;
            margin-top: -0.25rem;
            margin-bottom: 0.75rem;
        }
        .compare-panel {
            border: 1px solid rgba(49, 51, 63, 0.14);
            border-radius: 12px;
            padding: 0.85rem;
            background: #ffffff;
        }
        .compare-caption {
            font-size: 0.88rem;
            color: #5c6470;
            margin-top: 0.25rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_defaults() -> None:
    defaults = {
        "patient_id": "",
        "patient_name": "",
        "exam_date": date.today(),
        "diagnosis": "",
        "gait_mode": GAIT_MODE_OPTIONS[0],
        "support_stability": SUPPORT_OPTIONS[0],
        "step_width": STEP_WIDTH_OPTIONS[0],
        "video_fps": 30.0,
        "initial_contact_right": INITIAL_CONTACT_OPTIONS[0],
        "initial_contact_left": INITIAL_CONTACT_OPTIONS[0],
        "loading_response_right": LOADING_RESPONSE_OPTIONS[0],
        "loading_response_left": LOADING_RESPONSE_OPTIONS[0],
        "first_rocker_right": ROLLING_OPTIONS[0],
        "first_rocker_left": ROLLING_OPTIONS[0],
        "retrofoot_right": RETROFOOT_OPTIONS[0],
        "retrofoot_left": RETROFOOT_OPTIONS[0],
        "forefoot_right": FOREFOOT_OPTIONS[0],
        "forefoot_left": FOREFOOT_OPTIONS[0],
        "leg_advancement_right": LEG_ADVANCEMENT_OPTIONS[0],
        "leg_advancement_left": LEG_ADVANCEMENT_OPTIONS[0],
        "midstance_right": MIDSTANCE_OPTIONS[0],
        "midstance_left": MIDSTANCE_OPTIONS[0],
        "second_rocker_right": ROLLING_OPTIONS[0],
        "second_rocker_left": ROLLING_OPTIONS[0],
        "plantar_flexion_right": PLANTAR_FLEXION_OPTIONS[0],
        "plantar_flexion_left": PLANTAR_FLEXION_OPTIONS[0],
        "heel_off_right": HEEL_OFF_OPTIONS[0],
        "heel_off_left": HEEL_OFF_OPTIONS[0],
        "third_rocker_right": ROLLING_OPTIONS[0],
        "third_rocker_left": ROLLING_OPTIONS[0],
        "foot_progression_right": FOOT_PROGRESSION_OPTIONS[0],
        "foot_progression_left": FOOT_PROGRESSION_OPTIONS[0],
        "swing_progression_right": SWING_PROGRESSION_OPTIONS[0],
        "swing_progression_left": SWING_PROGRESSION_OPTIONS[0],
        "foot_clearance_right": FOOT_CLEARANCE_OPTIONS[0],
        "foot_clearance_left": FOOT_CLEARANCE_OPTIONS[0],
        "knee_initial_right": KNEE_FLEXION_OPTIONS[0],
        "knee_initial_left": KNEE_FLEXION_OPTIONS[0],
        "knee_midstance_right": KNEE_EXTENSION_OPTIONS[0],
        "knee_midstance_left": KNEE_EXTENSION_OPTIONS[0],
        "knee_pre_swing_right": KNEE_FLEXION_OPTIONS[0],
        "knee_pre_swing_left": KNEE_FLEXION_OPTIONS[0],
        "knee_swing_right": KNEE_FLEXION_OPTIONS[0],
        "knee_swing_left": KNEE_FLEXION_OPTIONS[0],
        "knee_terminal_right": KNEE_TERMINAL_OPTIONS[0],
        "knee_terminal_left": KNEE_TERMINAL_OPTIONS[0],
        "hip_initial_right": HIP_FLEXION_OPTIONS[0],
        "hip_initial_left": HIP_FLEXION_OPTIONS[0],
        "hip_terminal_right": HIP_EXTENSION_OPTIONS[0],
        "hip_terminal_left": HIP_EXTENSION_OPTIONS[0],
        "hip_swing_right": HIP_SWING_OPTIONS[0],
        "hip_swing_left": HIP_SWING_OPTIONS[0],
        "hip_frontal_stance_right": HIP_ADDUCTION_OPTIONS[0],
        "hip_frontal_stance_left": HIP_ADDUCTION_OPTIONS[0],
        "hip_frontal_swing_right": HIP_SWING_FRONTAL_OPTIONS[0],
        "hip_frontal_swing_left": HIP_SWING_FRONTAL_OPTIONS[0],
        "hip_rotation_right": HIP_ROTATION_OPTIONS[0],
        "hip_rotation_left": HIP_ROTATION_OPTIONS[0],
        "pelvis_tilt": PELVIS_TILT_OPTIONS[0],
        "pelvis_obliquity": PELVIS_OBLIQUITY_OPTIONS[0],
        "pelvis_rotation": PELVIS_ROTATION_OPTIONS[0],
        "trunk_position": TRUNK_POSITION_OPTIONS[0],
        "trunk_lean": TRUNK_LEAN_OPTIONS[0],
        "upper_limbs": UPPER_LIMB_OPTIONS[0],
        "additional_notes": "",
        "video_target_frame": 0,
        "calibration_horizontal_cm": 50.8,
        "calibration_oblique_cm": 50.8,
        "calibration_horizontal_x1": 584,
        "calibration_horizontal_y1": 982,
        "calibration_horizontal_x2": 993,
        "calibration_horizontal_y2": 1001,
        "calibration_oblique_x1": 586,
        "calibration_oblique_y1": 987,
        "calibration_oblique_x2": 657,
        "calibration_oblique_y2": 911,
        "comparison_frame": 0,
        "comparison_left_start": 0,
        "comparison_right_start": 0,
        "comparison_left_fps": 30.0,
        "comparison_right_fps": 30.0,
        "comparison_left_total_frames": 0,
        "comparison_right_total_frames": 0,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)
    st.session_state.setdefault("event_marker_values", {})
    for marker in EVENT_MARKERS:
        marker_key = f"marker_{marker['id']}"
        st.session_state.setdefault(marker_key, "")
    for marker in BILATERAL_TEMPORAL_MARKERS:
        marker_key = f"bilateral_marker_{marker['id']}"
        st.session_state.setdefault(marker_key, "")


def ensure_calibration_coordinate_defaults() -> None:
    calibration_defaults = {
        "calibration_horizontal_x1": 584,
        "calibration_horizontal_y1": 982,
        "calibration_horizontal_x2": 993,
        "calibration_horizontal_y2": 1001,
        "calibration_oblique_x1": 586,
        "calibration_oblique_y1": 987,
        "calibration_oblique_x2": 657,
        "calibration_oblique_y2": 911,
    }
    for key, value in calibration_defaults.items():
        current = st.session_state.get(key)
        if current in (None, "", 0):
            st.session_state[key] = value


def persist_event_markers() -> None:
    st.session_state["event_marker_values"] = {
        marker["id"]: str(st.session_state.get(f"marker_{marker['id']}", "")).strip()
        for marker in EVENT_MARKERS
    }


def jump_to_marker(marker_id: str) -> None:
    persist_event_markers()
    marker_value = str(st.session_state.get(f"marker_{marker_id}", "")).strip()
    if marker_value.isdigit():
        st.session_state.video_target_frame = int(marker_value)


def jump_to_value_key(value_key: str) -> None:
    marker_value = str(st.session_state.get(value_key, "")).strip()
    if marker_value.isdigit():
        st.session_state.video_target_frame = int(marker_value)


def apply_detected_calibration(result: object) -> None:
    horizontal = getattr(result, "horizontal_segment", None)
    oblique = getattr(result, "oblique_segment", None)
    if horizontal is not None:
        st.session_state["calibration_horizontal_x1"] = horizontal.x1
        st.session_state["calibration_horizontal_y1"] = horizontal.y1
        st.session_state["calibration_horizontal_x2"] = horizontal.x2
        st.session_state["calibration_horizontal_y2"] = horizontal.y2
    if oblique is not None:
        st.session_state["calibration_oblique_x1"] = oblique.x1
        st.session_state["calibration_oblique_y1"] = oblique.y1
        st.session_state["calibration_oblique_x2"] = oblique.x2
        st.session_state["calibration_oblique_y2"] = oblique.y2


def select_pair(label: str, key_right: str, key_left: str, options: list[str]) -> None:
    st.markdown(f"**{label}**")
    col_right, col_left = st.columns(2)
    with col_right:
        st.selectbox("Direita", options, key=key_right, label_visibility="visible")
    with col_left:
        st.selectbox("Esquerda", options, key=key_left, label_visibility="visible")


def render_header() -> None:
    st.title("Análise Observacional da Marcha no Vídeo")
    st.caption(
        "Vídeo fixo, formulário rolável, texto automático e exportação Word a partir da lógica da planilha LabMarch."
    )


def render_patient_block() -> None:
    st.subheader("Paciente e exame")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.text_input("Registro", key="patient_id")
    with col2:
        st.text_input("Nome", key="patient_name")
    with col3:
        st.date_input("Data", key="exam_date", format="DD/MM/YYYY")
    st.text_input("Diagnóstico", key="diagnosis")

    col4, col5, col6 = st.columns(3)
    with col4:
        st.selectbox("Marcha", GAIT_MODE_OPTIONS, key="gait_mode")
    with col5:
        st.selectbox("Apoio", SUPPORT_OPTIONS, key="support_stability")
    with col6:
        st.selectbox("Largura do passo", STEP_WIDTH_OPTIONS, key="step_width")


def step_video_frame(delta: int) -> None:
    current_frame = int(st.session_state.get("video_target_frame", 0) or 0)
    max_frame = int(st.session_state.get("video_total_frames", 0) or 0)
    upper_bound = max_frame - 1 if max_frame > 0 else current_frame + abs(delta)
    st.session_state.video_target_frame = min(max(0, current_frame + delta), max(0, upper_bound))


def _comparison_upper_bound() -> int:
    left_total = int(st.session_state.get("comparison_left_total_frames", 0) or 0)
    right_total = int(st.session_state.get("comparison_right_total_frames", 0) or 0)
    left_start = int(st.session_state.get("comparison_left_start", 0) or 0)
    right_start = int(st.session_state.get("comparison_right_start", 0) or 0)
    bounds = []
    if left_total > left_start:
        bounds.append(left_total - left_start - 1)
    if right_total > right_start:
        bounds.append(right_total - right_start - 1)
    return max(0, min(bounds)) if bounds else 0


def step_comparison_frame(delta: int) -> None:
    current_frame = int(st.session_state.get("comparison_frame", 0) or 0)
    upper_bound = _comparison_upper_bound()
    st.session_state.comparison_frame = min(max(0, current_frame + delta), upper_bound)


def update_comparison_metadata(uploaded_video, side: str) -> None:
    if uploaded_video is None:
        return
    signature_key = f"comparison_{side}_signature"
    upload_signature = f"{uploaded_video.name}:{uploaded_video.size}"
    if st.session_state.get(signature_key) == upload_signature:
        return

    metadata = read_video_metadata(uploaded_video.getvalue())
    if metadata.fps is not None:
        st.session_state[f"comparison_{side}_fps"] = round(metadata.fps, 3)
    if metadata.total_frames is not None:
        st.session_state[f"comparison_{side}_total_frames"] = metadata.total_frames
    st.session_state[signature_key] = upload_signature
    st.session_state.comparison_frame = 0


@st.cache_data(show_spinner=False)
def cached_frame_preview(video_bytes: bytes, frame_index: int) -> bytes | None:
    return extract_single_frame(video_bytes, frame_index)

@st.cache_data(show_spinner=False)
def _cached_frame_assets(video_bytes: bytes, markers: dict) -> object:
    return extract_frame_export_assets(video_bytes, markers)

@st.cache_data(show_spinner=False)
def _cached_infographic(temporal_results_key: str, side_rows_json: str, summary_json: str) -> bytes | None:
    """Cache chaveado pelo conteúdo dos resultados, não pelo objeto."""
    import json
    return None  # placeholder — infographic é gerado direto abaixo sem cache pesado


def render_keyboard_shortcuts() -> None:
    components.html(
        """
        <script>
        const doc = window.parent.document;
        if (!window.parent.__gaitArrowFrameHandlerBound) {
          window.parent.__gaitArrowFrameHandlerBound = true;
          window.parent.addEventListener("keydown", function(event) {
            const tag = (event.target && event.target.tagName ? event.target.tagName : "").toLowerCase();
            const isEditable = tag === "input" || tag === "textarea";
            if (isEditable) {
              return;
            }

            const buttons = Array.from(doc.querySelectorAll("button"));
            const prevButton = buttons.find((button) => button.innerText.includes("◀ 1 frame"));
            const nextButton = buttons.find((button) => button.innerText.includes("1 frame ▶"));

            if (event.key === "ArrowLeft" && prevButton) {
              event.preventDefault();
              prevButton.click();
            }
            if (event.key === "ArrowRight" && nextButton) {
              event.preventDefault();
              nextButton.click();
            }
          });
        }
        </script>
        """,
        height=0,
        width=0,
    )


def render_comparison_keyboard_shortcuts() -> None:
    components.html(
        """
        <script>
        const doc = window.parent.document;
        if (!window.parent.__gaitCompareArrowHandlerBound) {
          window.parent.__gaitCompareArrowHandlerBound = true;
          window.parent.addEventListener("keydown", function(event) {
            const tag = (event.target && event.target.tagName ? event.target.tagName : "").toLowerCase();
            const isEditable = tag === "input" || tag === "textarea";
            if (isEditable) {
              return;
            }

            const buttons = Array.from(doc.querySelectorAll("button"));
            const prevButton = buttons.find((button) => button.innerText.includes("Comparar ◀ 1 frame"));
            const nextButton = buttons.find((button) => button.innerText.includes("Comparar 1 frame ▶"));

            if (event.key === "ArrowLeft" && prevButton) {
              event.preventDefault();
              prevButton.click();
            }
            if (event.key === "ArrowRight" && nextButton) {
              event.preventDefault();
              nextButton.click();
            }
          });
        }
        </script>
        """,
        height=0,
        width=0,
    )


def render_video_player(uploaded_video) -> None:
    fps = float(st.session_state.video_fps)
    current_frame = int(st.session_state.get("video_target_frame", 0) or 0)
    current_time_seconds = current_frame / fps if fps > 0 else 0.0
    total_frames = int(st.session_state.get("video_total_frames", 0) or 0)

    control_col1, control_col2, control_col3, control_col4, control_col5 = st.columns([1, 1, 1.2, 1.1, 1.1])
    with control_col1:
        st.button("◀ 1 frame", on_click=step_video_frame, args=(-1,), use_container_width=True)
    with control_col2:
        st.button("1 frame ▶", on_click=step_video_frame, args=(1,), use_container_width=True)
    with control_col3:
        st.number_input("Frame atual", min_value=0, step=1, key="video_target_frame")
    with control_col4:
        st.metric("Tempo alvo", f"{current_time_seconds:.3f} s")
    with control_col5:
        st.metric("Total de frames", total_frames if total_frames > 0 else "-")

    render_keyboard_shortcuts()
    st.video(uploaded_video, start_time=current_time_seconds)
    frame_preview = cached_frame_preview(uploaded_video.getvalue(), current_frame)
    if frame_preview is not None:
        st.image(frame_preview, caption=f"Frame {current_frame}", use_container_width=True)


def render_event_markers() -> None:
    with st.expander("Eventos bilaterais para variáveis temporais e assimetria", expanded=True):
        st.caption(
            "Use esta sequência bilateral para calcular apoio, balanço, duplos apoios, apoio simples e variáveis direito/esquerdo."
        )
        bilateral_cols = st.columns(4)
        for index, marker in enumerate(BILATERAL_TEMPORAL_MARKERS):
            key = f"bilateral_marker_{marker['id']}"
            with bilateral_cols[index % 4]:
                st.text_input(marker["label"], key=key, placeholder="frame")
                marker_value = str(st.session_state.get(key, "")).strip()
                st.button(
                    "Ir",
                    key=f"jump_bilateral_{marker['id']}",
                    disabled=not marker_value.isdigit(),
                    use_container_width=True,
                    on_click=jump_to_value_key,
                    args=(key,),
                )

    with st.expander("Marcação opcional dos eventos do ciclo em frames", expanded=False):
        st.caption(
            "Preencha o frame de cada evento se quiser documentar o ciclo e usar esses marcos como atalhos para navegar no vídeo."
        )
        marker_cols = st.columns(4)
        for index, marker in enumerate(EVENT_MARKERS):
            key = f"marker_{marker['id']}"
            with marker_cols[index % 4]:
                st.text_input(marker["label"], key=key, placeholder="frame")
                marker_value = str(st.session_state.get(key, "")).strip()
                can_jump = marker_value.isdigit()
                st.button(
                    "Ir",
                    key=f"jump_{marker['id']}",
                    disabled=not can_jump,
                    use_container_width=True,
                    on_click=jump_to_marker,
                    args=(marker["id"],),
                )
        persist_event_markers()


def render_video_block() -> str:
    st.subheader("Vídeo")
    uploaded_video = st.file_uploader(
        "Importe o vídeo do paciente",
        type=["mp4", "mov", "avi", "m4v", "mpeg"],
        key="video_upload",
    )
    if uploaded_video is not None:
        upload_signature = f"{uploaded_video.name}:{uploaded_video.size}"
        previous_signature = st.session_state.get("video_upload_signature")
        if upload_signature != previous_signature:
            metadata = read_video_metadata(uploaded_video.getvalue())
            detected_fps = metadata.fps
            if detected_fps is not None:
                st.session_state.video_fps = round(detected_fps, 3)
            if metadata.total_frames is not None:
                st.session_state.video_total_frames = metadata.total_frames
            st.session_state.video_upload_signature = upload_signature
            st.session_state.video_target_frame = 0
            st.rerun()

    if uploaded_video is not None:
        st.markdown('<div class="video-shell">', unsafe_allow_html=True)
        render_video_player(uploaded_video)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown(
            '<div class="video-caption">Use os botões para avançar frame a frame e os marcadores do ciclo para saltar entre eventos. Nesta versão, o vídeo fica em uma coluna fixa enquanto o formulário rola na coluna ao lado.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("Importe um vídeo acima para abrir o player.")

    st.number_input("FPS do vídeo", min_value=1.0, max_value=240.0, step=1.0, key="video_fps")
    if uploaded_video is not None:
        st.caption(f"FPS detectado do arquivo: {st.session_state.video_fps}")

    video_name = uploaded_video.name if uploaded_video else ""
    return video_name


def render_calibration_module() -> None:
    with st.expander("Calibração da plataforma", expanded=False):
        ensure_calibration_coordinate_defaults()
        st.caption(
            "Use uma imagem de referência com as faixas pretas desenhadas. O app detecta os segmentos, calcula a escala em pixels por centímetro e guarda esse valor para os parâmetros lineares."
        )
        st.info(
            "Valores atuais da sua referência: 50,8 cm para a faixa horizontal e 50,8 cm para a faixa oblíqua."
        )
        calibration_image = st.file_uploader(
            "Imagem de calibração",
            type=["png", "jpg", "jpeg"],
            key="calibration_image_upload",
        )
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Comprimento real da faixa horizontal (cm)", min_value=0.1, step=0.1, key="calibration_horizontal_cm")
        with col2:
            st.number_input("Comprimento real da faixa oblíqua (cm)", min_value=0.1, step=0.1, key="calibration_oblique_cm")

        if calibration_image is None:
            st.info("Envie a imagem anotada da plataforma para gerar a escala inicial.")
            return

        result = analyze_calibration_image(calibration_image.getvalue())
        st.button(
            "Usar detecção automática nesta imagem",
            on_click=apply_detected_calibration,
            args=(result,),
            use_container_width=True,
        )

        adjusted_horizontal = None
        adjusted_oblique = None

        st.markdown("**Ajuste manual da faixa horizontal**")
        h1, h2, h3, h4 = st.columns(4)
        with h1:
            st.number_input("x1 horizontal", min_value=0, step=1, key="calibration_horizontal_x1")
        with h2:
            st.number_input("y1 horizontal", min_value=0, step=1, key="calibration_horizontal_y1")
        with h3:
            st.number_input("x2 horizontal", min_value=0, step=1, key="calibration_horizontal_x2")
        with h4:
            st.number_input("y2 horizontal", min_value=0, step=1, key="calibration_horizontal_y2")
        hx1 = int(st.session_state.calibration_horizontal_x1)
        hy1 = int(st.session_state.calibration_horizontal_y1)
        hx2 = int(st.session_state.calibration_horizontal_x2)
        hy2 = int(st.session_state.calibration_horizontal_y2)
        adjusted_horizontal = DetectedSegment(
            x1=hx1,
            y1=hy1,
            x2=hx2,
            y2=hy2,
            length_px=((hx2 - hx1) ** 2 + (hy2 - hy1) ** 2) ** 0.5,
        )

        st.markdown("**Ajuste manual da faixa oblíqua**")
        o1, o2, o3, o4 = st.columns(4)
        with o1:
            st.number_input("x1 oblíqua", min_value=0, step=1, key="calibration_oblique_x1")
        with o2:
            st.number_input("y1 oblíqua", min_value=0, step=1, key="calibration_oblique_y1")
        with o3:
            st.number_input("x2 oblíqua", min_value=0, step=1, key="calibration_oblique_x2")
        with o4:
            st.number_input("y2 oblíqua", min_value=0, step=1, key="calibration_oblique_y2")
        ox1 = int(st.session_state.calibration_oblique_x1)
        oy1 = int(st.session_state.calibration_oblique_y1)
        ox2 = int(st.session_state.calibration_oblique_x2)
        oy2 = int(st.session_state.calibration_oblique_y2)
        adjusted_oblique = DetectedSegment(
            x1=ox1,
            y1=oy1,
            x2=ox2,
            y2=oy2,
            length_px=((ox2 - ox1) ** 2 + (oy2 - oy1) ** 2) ** 0.5,
        )

        preview_bytes = build_calibration_preview(calibration_image.getvalue(), adjusted_horizontal, adjusted_oblique)
        st.image(preview_bytes, caption="Linhas usadas na calibração", use_container_width=True)
        st.caption(
            "Se a linha automática ficou menor do que a faixa desenhada, ajuste os pontos acima. Uma linha curta demais aumenta artificialmente a velocidade calculada."
        )

        rows: list[dict[str, str | float]] = []
        scales: list[float] = []
        if adjusted_horizontal is not None:
            px_per_cm = adjusted_horizontal.length_px / float(st.session_state.calibration_horizontal_cm)
            scales.append(px_per_cm)
            rows.append(
                {
                    "Referência": "Horizontal",
                    "Comprimento detectado (px)": round(adjusted_horizontal.length_px, 2),
                    "Comprimento real (cm)": float(st.session_state.calibration_horizontal_cm),
                    "Escala (px/cm)": round(px_per_cm, 4),
                }
            )
        if adjusted_oblique is not None:
            px_per_cm = adjusted_oblique.length_px / float(st.session_state.calibration_oblique_cm)
            scales.append(px_per_cm)
            rows.append(
                {
                    "Referência": "Oblíqua",
                    "Comprimento detectado (px)": round(adjusted_oblique.length_px, 2),
                    "Comprimento real (cm)": float(st.session_state.calibration_oblique_cm),
                    "Escala (px/cm)": round(px_per_cm, 4),
                }
            )

        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
        if scales:
            mean_scale = sum(scales) / len(scales)
            st.metric("Escala média inicial", f"{mean_scale:.4f} px/cm")
            st.session_state["platform_scale_px_per_cm"] = mean_scale
            st.success("Escala salva para a próxima etapa dos parâmetros lineares.")
        else:
            st.warning("Não consegui detectar automaticamente as duas faixas pretas nesta imagem.")


def render_analysis_form() -> None:
    tab_foot, tab_knee, tab_hip, tab_pelvis, tab_trunk = st.tabs(
        ["Pé/Tornozelo", "Joelho", "Quadril", "Pelve", "Tronco/MMSS"]
    )

    with tab_foot:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        select_pair("Contato inicial", "initial_contact_right", "initial_contact_left", INITIAL_CONTACT_OPTIONS)
        select_pair("Resposta à carga", "loading_response_right", "loading_response_left", LOADING_RESPONSE_OPTIONS)
        select_pair("Primeiro mecanismo de rolamento", "first_rocker_right", "first_rocker_left", ROLLING_OPTIONS)
        st.markdown("**Neste instante há**")
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Retropé direito", RETROFOOT_OPTIONS, key="retrofoot_right")
            st.selectbox("Antepé direito", FOREFOOT_OPTIONS, key="forefoot_right")
        with col2:
            st.selectbox("Retropé esquerdo", RETROFOOT_OPTIONS, key="retrofoot_left")
            st.selectbox("Antepé esquerdo", FOREFOOT_OPTIONS, key="forefoot_left")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        select_pair("Avanço da perna sobre o pé", "leg_advancement_right", "leg_advancement_left", LEG_ADVANCEMENT_OPTIONS)
        select_pair("Médio apoio", "midstance_right", "midstance_left", MIDSTANCE_OPTIONS)
        select_pair("Segundo mecanismo de rolamento", "second_rocker_right", "second_rocker_left", ROLLING_OPTIONS)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        select_pair(
            "Flexão plantar no pré-balanço",
            "plantar_flexion_right",
            "plantar_flexion_left",
            PLANTAR_FLEXION_OPTIONS,
        )
        select_pair("Desprendimento do calcanhar", "heel_off_right", "heel_off_left", HEEL_OFF_OPTIONS)
        select_pair("Terceiro mecanismo de rolamento", "third_rocker_right", "third_rocker_left", ROLLING_OPTIONS)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        select_pair(
            "Progressão do pé no apoio",
            "foot_progression_right",
            "foot_progression_left",
            FOOT_PROGRESSION_OPTIONS,
        )
        select_pair(
            "Ângulo de progressão no balanço",
            "swing_progression_right",
            "swing_progression_left",
            SWING_PROGRESSION_OPTIONS,
        )
        select_pair("Liberação do pé", "foot_clearance_right", "foot_clearance_left", FOOT_CLEARANCE_OPTIONS)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_knee:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        select_pair("Joelho no contato inicial", "knee_initial_right", "knee_initial_left", KNEE_FLEXION_OPTIONS)
        select_pair("Joelho no apoio simples", "knee_midstance_right", "knee_midstance_left", KNEE_EXTENSION_OPTIONS)
        select_pair("Joelho no pré-balanço", "knee_pre_swing_right", "knee_pre_swing_left", KNEE_FLEXION_OPTIONS)
        select_pair("Joelho no balanço", "knee_swing_right", "knee_swing_left", KNEE_FLEXION_OPTIONS)
        select_pair(
            "Joelho no balanço terminal",
            "knee_terminal_right",
            "knee_terminal_left",
            KNEE_TERMINAL_OPTIONS,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_hip:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        select_pair("Quadril no contato inicial", "hip_initial_right", "hip_initial_left", HIP_FLEXION_OPTIONS)
        select_pair("Quadril no apoio terminal", "hip_terminal_right", "hip_terminal_left", HIP_EXTENSION_OPTIONS)
        select_pair("Quadril no balanço", "hip_swing_right", "hip_swing_left", HIP_SWING_OPTIONS)
        select_pair(
            "Quadril no plano frontal durante o apoio",
            "hip_frontal_stance_right",
            "hip_frontal_stance_left",
            HIP_ADDUCTION_OPTIONS,
        )
        select_pair(
            "Quadril no plano frontal durante o balanço",
            "hip_frontal_swing_right",
            "hip_frontal_swing_left",
            HIP_SWING_FRONTAL_OPTIONS,
        )
        select_pair("Rotações da coxa", "hip_rotation_right", "hip_rotation_left", HIP_ROTATION_OPTIONS)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_pelvis:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.selectbox("Anteversão", PELVIS_TILT_OPTIONS, key="pelvis_tilt")
        st.selectbox("Inclinação", PELVIS_OBLIQUITY_OPTIONS, key="pelvis_obliquity")
        st.selectbox("Rotação", PELVIS_ROTATION_OPTIONS, key="pelvis_rotation")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_trunk:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.selectbox("Posição do tronco", TRUNK_POSITION_OPTIONS, key="trunk_position")
        st.selectbox("Inclinação lateral do tronco", TRUNK_LEAN_OPTIONS, key="trunk_lean")
        st.selectbox("Membros superiores", UPPER_LIMB_OPTIONS, key="upper_limbs")
        st.text_area(
            "Observações adicionais",
            key="additional_notes",
            placeholder="Anote observações livres que não entram nas opções padrão.",
            height=120,
        )
        st.markdown("</div>", unsafe_allow_html=True)


def current_form_data() -> dict[str, str]:
    data: dict[str, str] = {}
    for key, value in st.session_state.items():
        if key == "exam_date" and isinstance(value, date):
            data[key] = value.strftime("%d/%m/%Y")
        elif key.startswith("marker_") or key.startswith("bilateral_marker_"):
            continue
        else:
            data[key] = str(value)
    return data


def marker_map() -> dict[str, str]:
    return {
        marker["label"]: str(st.session_state.get(f"marker_{marker['id']}", "")).strip()
        for marker in EVENT_MARKERS
    }


def bilateral_marker_map() -> dict[str, str]:
    return {
        marker["label"]: str(st.session_state.get(f"bilateral_marker_{marker['id']}", "")).strip()
        for marker in BILATERAL_TEMPORAL_MARKERS
    }


def render_output(video_name: str, uploaded_video) -> None:
    form_data = current_form_data()
    paragraphs = build_report_text(form_data)
    markers = marker_map()
    bilateral_markers = bilateral_marker_map()
    temporal_results = compute_temporal_parameters(markers, float(st.session_state.video_fps), bilateral_markers)
    temporal_infographic_bytes = build_temporal_infographic(temporal_results)
    frame_assets = _cached_frame_assets(uploaded_video.getvalue(), markers) if uploaded_video is not None else None
    frame_snapshots = frame_assets.snapshots if frame_assets is not None else []
    frame_montage_bytes = frame_assets.montage_bytes if frame_assets is not None else None

    st.subheader("Conferência final")
    st.caption("Revise aqui o texto que será exportado antes de baixar o arquivo Word.")
    report_text = compact_lines(paragraphs)
    preview_html = "<br><br>".join(paragraph.replace("\n", " ") for paragraph in paragraphs)
    st.markdown(
        f"""
        <div style="border:1px solid rgba(49,51,63,0.18); border-radius:14px; padding:16px; background:#fff; line-height:1.6;">
            {preview_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if temporal_results.event_rows:
        st.subheader("Painel temporal")
        if temporal_results.source_mode == "bilateral":
            st.caption("Painel priorizando os eventos bilaterais espaciotemporais para calcular variáveis direito/esquerdo.")
        else:
            st.caption("Painel baseado nos eventos gerais do ciclo. Preencha a seção bilateral para métricas direito/esquerdo mais precisas.")
        summary_cols = st.columns(3)
        with summary_cols[0]:
            if temporal_results.summary.observed_cycle_seconds is not None:
                st.metric(
                    "Janela observada",
                    f"{temporal_results.summary.observed_cycle_seconds:.3f} s",
                    f"{temporal_results.summary.observed_cycle_frames} frames",
                )
        with summary_cols[1]:
            if temporal_results.summary.support_window_seconds is not None:
                st.metric(
                    "Apoio observado",
                    f"{temporal_results.summary.support_window_seconds:.3f} s",
                    f"{temporal_results.summary.support_window_frames} frames",
                )
        with summary_cols[2]:
            if temporal_results.summary.swing_window_seconds is not None:
                st.metric(
                    "Balanço observado",
                    f"{temporal_results.summary.swing_window_seconds:.3f} s",
                    f"{temporal_results.summary.swing_window_frames} frames",
                )
        if temporal_infographic_bytes:
            st.image(
                temporal_infographic_bytes,
                caption="Infográfico temporal gerado a partir dos eventos marcados",
                use_container_width=True,
            )
        if temporal_results.side_rows:
            st.dataframe(temporal_results.side_rows, use_container_width=True, hide_index=True)

    if frame_snapshots:
        st.caption(
            f"{len(frame_snapshots)} frame(s) marcado(s) serão anexados automaticamente ao documento, na ordem do ciclo de marcha."
        )
    if frame_montage_bytes:
        st.image(frame_montage_bytes, caption="Prévia da sequência de frames exportada", use_container_width=True)

    export_data = ReportData(
        title="Análise Observacional da Marcha no Vídeo",
        patient_name=form_data["patient_name"],
        patient_id=form_data["patient_id"],
        exam_date=form_data["exam_date"],
        diagnosis=form_data["diagnosis"],
        video_name=video_name,
        markers={**markers, **bilateral_markers},
        paragraphs=paragraphs,
        notes=form_data["additional_notes"],
        frame_snapshots=frame_snapshots,
        frame_montage_bytes=frame_montage_bytes,
        temporal_results=temporal_results,
        temporal_infographic_bytes=temporal_infographic_bytes,
    )
    filename_stub = form_data["patient_name"].strip().replace(" ", "_") or "paciente"
    st.download_button(
        "Exportar para Word (.docx)",
        data=build_docx_bytes(export_data),
        file_name=f"analise_marcha_{filename_stub}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


def _render_comparison_video_panel(uploaded_video, side: str, title: str) -> None:
    st.markdown(f"**{title}**")
    if uploaded_video is None:
        st.info("Importe um vídeo para comparar.")
        return

    shared_frame = int(st.session_state.get("comparison_frame", 0) or 0)
    start_frame = int(st.session_state.get(f"comparison_{side}_start", 0) or 0)
    frame_index = max(0, start_frame + shared_frame)
    fps = float(st.session_state.get(f"comparison_{side}_fps", 30.0) or 30.0)
    total_frames = int(st.session_state.get(f"comparison_{side}_total_frames", 0) or 0)
    time_seconds = frame_index / fps if fps > 0 else 0.0

    frame_preview = cached_frame_preview(uploaded_video.getvalue(), frame_index)
    if frame_preview is not None:
        st.image(frame_preview, caption=f"Frame {frame_index} | {time_seconds:.3f} s", use_container_width=True)
    else:
        st.warning("Não consegui extrair este frame do vídeo.")

    metric_cols = st.columns(3)
    with metric_cols[0]:
        st.metric("Frame", frame_index)
    with metric_cols[1]:
        st.metric("Tempo", f"{time_seconds:.3f} s")
    with metric_cols[2]:
        st.metric("Total", total_frames if total_frames > 0 else "-")


def render_video_comparison_page() -> None:
    st.title("Comparação de Vídeos")
    st.caption("Compare dois vídeos em paralelo com avanço frame a frame sincronizado.")

    upload_col1, upload_col2 = st.columns(2, gap="large")
    with upload_col1:
        left_video = st.file_uploader(
            "Vídeo 1",
            type=["mp4", "mov", "avi", "m4v", "mpeg"],
            key="comparison_left_upload",
        )
    with upload_col2:
        right_video = st.file_uploader(
            "Vídeo 2",
            type=["mp4", "mov", "avi", "m4v", "mpeg"],
            key="comparison_right_upload",
        )

    update_comparison_metadata(left_video, "left")
    update_comparison_metadata(right_video, "right")
    upper_bound = _comparison_upper_bound()
    current_comparison_frame = int(st.session_state.get("comparison_frame", 0) or 0)
    if current_comparison_frame > upper_bound:
        st.session_state.comparison_frame = upper_bound

    control_cols = st.columns([1, 1, 1.1, 1.1, 1.1, 1.1], gap="small")
    with control_cols[0]:
        st.button("Comparar ◀ 1 frame", on_click=step_comparison_frame, args=(-1,), use_container_width=True)
    with control_cols[1]:
        st.button("Comparar 1 frame ▶", on_click=step_comparison_frame, args=(1,), use_container_width=True)
    with control_cols[2]:
        st.number_input("Frame sincronizado", min_value=0, max_value=max(0, upper_bound), step=1, key="comparison_frame")
    with control_cols[3]:
        st.number_input("Início vídeo 1", min_value=0, step=1, key="comparison_left_start")
    with control_cols[4]:
        st.number_input("Início vídeo 2", min_value=0, step=1, key="comparison_right_start")
    with control_cols[5]:
        st.metric("Limite comum", upper_bound if upper_bound > 0 else "-")

    fps_cols = st.columns(2, gap="large")
    with fps_cols[0]:
        st.number_input("FPS vídeo 1", min_value=1.0, max_value=240.0, step=1.0, key="comparison_left_fps")
    with fps_cols[1]:
        st.number_input("FPS vídeo 2", min_value=1.0, max_value=240.0, step=1.0, key="comparison_right_fps")

    render_comparison_keyboard_shortcuts()

    video_col1, video_col2 = st.columns(2, gap="large")
    with video_col1:
        st.markdown('<div class="compare-panel">', unsafe_allow_html=True)
        _render_comparison_video_panel(left_video, "left", "Vídeo 1")
        st.markdown("</div>", unsafe_allow_html=True)
    with video_col2:
        st.markdown('<div class="compare-panel">', unsafe_allow_html=True)
        _render_comparison_video_panel(right_video, "right", "Vídeo 2")
        st.markdown("</div>", unsafe_allow_html=True)


def render_sidebar() -> None:
    st.sidebar.radio(
        "Página",
        ["Análise observacional", "Comparação de vídeos"],
        key="app_page",
    )
    if st.sidebar.button("Limpar formulario"):
        keys_to_reset = list(st.session_state.keys())
        for key in keys_to_reset:
            del st.session_state[key]
        st.rerun()


def render_analysis_page() -> None:
    render_header()
    st.markdown('<div class="center-block">', unsafe_allow_html=True)
    render_patient_block()
    video_col, form_col = st.columns([1.05, 1.15], gap="large")
    with video_col:
        st.markdown('<div class="left-sticky">', unsafe_allow_html=True)
        video_name = render_video_block()
        uploaded_video = st.session_state.get("video_upload")
        st.markdown("</div>", unsafe_allow_html=True)
    with form_col:
        st.markdown(
            '<div class="right-note">A coluna da direita pode ser rolada independentemente para preencher as opções enquanto o vídeo permanece visível à esquerda.</div>',
            unsafe_allow_html=True,
        )
        form_container = st.container(height=820, border=False)
        with form_container:
            render_calibration_module()
            render_event_markers()
            render_analysis_form()
    render_output(video_name, uploaded_video)
    st.markdown("</div>", unsafe_allow_html=True)
    st.caption(f"Última atualização da base: {datetime.now().strftime('%d/%m/%Y %H:%M')}")


def main() -> None:
    init_defaults()
    inject_styles()
    render_sidebar()
    if st.session_state.get("app_page") == "Comparação de vídeos":
        render_video_comparison_page()
    else:
        render_analysis_page()


if __name__ == "__main__":
    main()
