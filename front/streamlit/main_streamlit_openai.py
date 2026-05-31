import sys
from pathlib import Path
from typing import Literal, TypedDict

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import get_settings  # noqa: E402
from app.responses.estimate_llmwrapper_advanced_responses import (  # noqa: E402
    EstimationLLMWrapperAdvancedResponse,
)
from app.responses.estimate_responses import EstimateResponse  # noqa: E402
from front.streamlit.client.estimate_openai_client import (  # noqa: E402
    EstimateBackendError,
    EstimateOpenAIBackendClient,
)

CHAT_MESSAGES_KEY = "estimate_chat_messages"
ESTIMATION_MODE_KEY = "estimate_estimation_mode"
LLMWRAPPER_MODE_KEY = "estimate_llmwrapper_mode"
PROJECT_TYPE_KEY = "estimate_project_type"
DETAIL_LEVEL_KEY = "estimate_detail_level"
OUTPUT_FORMAT_KEY = "estimate_output_format"

PREDEFINED_PROMPT_TEXT = """
El cliente solicita una aplicación móvil para gestionar reservas de salas de reuniones en una empresa. La app debe permitir a los
empleados ver la disponibilidad, reservar, cancelar y recibir notificaciones. Se requiere autenticación corporativa, integración
con el calendario de Outlook y panel de administración web para métricas.
"""

ChatRole = Literal["user", "assistant"]
EstimationMode = Literal["openai", "llmwrapper"]
LLMWrapperMode = Literal["advanced"]


class ChatMessage(TypedDict):
    role: ChatRole
    content: str
    caption: str | None


class EstimationOptions(TypedDict):
    mode: EstimationMode
    llmwrapper_mode: LLMWrapperMode
    project_type: str
    detail_level: str
    output_format: str


PROJECT_TYPE_OPTIONS = {
    "SaaS web": "web_saas",
    "App móvil": "mobile_app",
    "Herramienta interna": "internal_tool",
    "Pipeline de datos": "data_pipeline",
}

DETAIL_LEVEL_OPTIONS = {
    "Resumen": "summary",
    "Medio": "medium",
    "Detallado": "detailed",
}

OUTPUT_FORMAT_OPTIONS = {
    "Tabla por fases": "phases_table",
    "Partidas": "line_items",
    "Narrativa": "narrative",
}


@st.cache_resource
def get_estimate_openai_client(
    base_url: str,
    timeout_seconds: float,
) -> EstimateOpenAIBackendClient:
    return EstimateOpenAIBackendClient(
        base_url=base_url,
        timeout_seconds=timeout_seconds,
    )


def initialize_chat_state() -> None:
    if CHAT_MESSAGES_KEY not in st.session_state:
        st.session_state[CHAT_MESSAGES_KEY] = []
    st.session_state.setdefault(ESTIMATION_MODE_KEY, "openai")
    st.session_state.setdefault(LLMWRAPPER_MODE_KEY, "Advanced")
    st.session_state.setdefault(PROJECT_TYPE_KEY, "SaaS web")
    st.session_state.setdefault(DETAIL_LEVEL_KEY, "Medio")
    st.session_state.setdefault(OUTPUT_FORMAT_KEY, "Tabla por fases")


def append_message(
    role: ChatRole,
    content: str,
    caption: str | None = None,
) -> None:
    message: ChatMessage = {
        "role": role,
        "content": content,
        "caption": caption,
    }
    st.session_state[CHAT_MESSAGES_KEY] = [
        *st.session_state[CHAT_MESSAGES_KEY],
        message,
    ]


def render_message(message: ChatMessage) -> None:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["caption"]:
            st.caption(message["caption"])


def render_chat_history() -> None:
    for message in st.session_state[CHAT_MESSAGES_KEY]:
        render_message(message)


def build_estimate_caption(response: EstimateResponse) -> str:
    caption_parts = [
        f"Proveedor: {response.provider}",
        f"Modelo: {response.llm_model}",
    ]

    if response.metadata and response.metadata.token_metadata:
        tokens = response.metadata.token_metadata
        caption_parts.append(f"Tokens: {tokens.num_tokens_total}")

    return " · ".join(caption_parts)


def build_advanced_estimate_caption(response: EstimationLLMWrapperAdvancedResponse) -> str:
    caption_parts = [
        "Motor: LLMWrapper Advanced",
        f"Prompt: {response.prompt_version}",
        f"Cache: {'sí' if response.cached else 'no'}",
        f"Confianza: {response.result.confidence_pct}%",
    ]
    return " · ".join(caption_parts)


def render_advanced_estimation(response: EstimationLLMWrapperAdvancedResponse) -> str:
    result = response.result
    lines = [
        result.summary,
        "",
        "| Fase | Semanas | Coste EUR | Resumen |",
        "| --- | ---: | ---: | --- |",
    ]
    for phase in result.phases:
        summary = phase.summary.replace("\n", " ")
        lines.append(
            f"| {phase.name} | {phase.duration_weeks} | {phase.cost_eur:,} | {summary} |"
        )
    lines.extend(
        [
            "",
            f"**Duración total:** {result.total_duration_weeks} semanas",
            f"**Coste total:** {result.total_cost_eur:,} EUR",
            f"**Confianza:** {result.confidence_pct}%",
        ]
    )
    return "\n".join(lines)


def request_estimation(
    client: EstimateOpenAIBackendClient,
    transcription: str,
    options: EstimationOptions,
) -> tuple[str, str]:
    if options["mode"] == "llmwrapper" and options["llmwrapper_mode"] == "advanced":
        response = client.estimate_advanced(
            description=transcription,
            project_type=options["project_type"],
            detail_level=options["detail_level"],
            output_format=options["output_format"],
        )
        return render_advanced_estimation(response), build_advanced_estimate_caption(response)

    response = client.estimate_from_transcript(transcription)
    return response.estimation, build_estimate_caption(response)


def process_transcription(transcription: str, options: EstimationOptions) -> None:
    normalized_transcription = transcription.strip()

    if not normalized_transcription:
        st.warning("La transcripción no puede estar vacía.")
        return

    append_message("user", normalized_transcription)
    render_message(st.session_state[CHAT_MESSAGES_KEY][-1])

    with st.chat_message("assistant"):
        with st.spinner("Generando estimación..."):
            try:
                estimation, caption = request_estimation(
                    estimate_client,
                    normalized_transcription,
                    options,
                )
            except EstimateBackendError as exc:
                estimation = str(exc)
                caption = None

        st.markdown(estimation)
        if caption:
            st.caption(caption)

    append_message("assistant", estimation, caption)


# Function to configure the Streamlit page layout and settings
def configure_page():
    st.set_page_config(
        page_title="Estimador CAG",
        page_icon="🤖",
        layout="centered",
        initial_sidebar_state="expanded",
    )

    st.title("💬 Estimador CAG")
    st.caption("Pega una transcripción de reunión y recibirás una estimación de software generada por el backend del proyecto.")

    return st.empty()


# Function to display and handle sidebar interactions
def handle_sidebar():
    selected_options: EstimationOptions

    with st.sidebar:
        st.subheader("Sesión")
        if st.button("Limpiar conversación", use_container_width=True):
            st.session_state[CHAT_MESSAGES_KEY] = []
            st.rerun()

        if st.button("Cargar prompt predefinido", use_container_width=True):
            selected_transcription = PREDEFINED_PROMPT_TEXT
        else:
            selected_transcription = None

        st.divider()
        st.subheader("Estimador")
        mode_label = st.selectbox(
            "Motor",
            options=["OpenAI", "LLMWrapper"],
            index=0 if st.session_state[ESTIMATION_MODE_KEY] == "openai" else 1,
            key="estimate_mode_selectbox",
        )
        mode: EstimationMode = "llmwrapper" if mode_label == "LLMWrapper" else "openai"
        st.session_state[ESTIMATION_MODE_KEY] = mode

        llmwrapper_mode: LLMWrapperMode = "advanced"
        if mode == "llmwrapper":
            st.selectbox(
                "Modo LLMWrapper",
                options=["Advanced"],
                index=0,
                key=LLMWRAPPER_MODE_KEY,
            )

            project_type_label = st.selectbox(
                "Tipo de proyecto",
                options=list(PROJECT_TYPE_OPTIONS),
                key=PROJECT_TYPE_KEY,
            )
            detail_level_label = st.selectbox(
                "Nivel de detalle",
                options=list(DETAIL_LEVEL_OPTIONS),
                key=DETAIL_LEVEL_KEY,
            )
            output_format_label = st.selectbox(
                "Formato de salida",
                options=list(OUTPUT_FORMAT_OPTIONS),
                key=OUTPUT_FORMAT_KEY,
            )
        else:
            project_type_label = st.session_state[PROJECT_TYPE_KEY]
            detail_level_label = st.session_state[DETAIL_LEVEL_KEY]
            output_format_label = st.session_state[OUTPUT_FORMAT_KEY]

        selected_options = {
            "mode": mode,
            "llmwrapper_mode": llmwrapper_mode,
            "project_type": PROJECT_TYPE_OPTIONS[project_type_label],
            "detail_level": DETAIL_LEVEL_OPTIONS[detail_level_label],
            "output_format": OUTPUT_FORMAT_OPTIONS[output_format_label],
        }

    return selected_transcription, selected_options


# =====================
# Load environment
# =====================

settings = get_settings()

# =====================
# Client Configuration
# =====================

estimate_client = get_estimate_openai_client(
    settings.ESTIMATE_BACKEND_BASE_URL,
    settings.ESTIMATE_BACKEND_TIMEOUT_SECONDS,
)

# =====================
# Execution
# =====================

debug_placeholder = configure_page()

initialize_chat_state()

sidebar_transcription, estimation_options = handle_sidebar()

render_chat_history()

transcription = st.chat_input("Escribe o pega la transcripción de la reunión")

if sidebar_transcription:
    process_transcription(sidebar_transcription, estimation_options)
elif transcription:
    process_transcription(transcription, estimation_options)

with debug_placeholder.container():
    with st.expander("Check State"):
        st.write(st.session_state)
