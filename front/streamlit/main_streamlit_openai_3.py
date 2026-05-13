import sys
import time
from pathlib import Path
from typing import Literal, TypedDict

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import get_settings  # noqa: E402
from app.context.estimate_prompts import SYSTEM_PROMPT  # noqa: E402
from app.context.basic_examples import BASIC_ESTIMATION_EXAMPLES, format_examples_for_prompt  # noqa: E402
from app.responses.estimate_responses import EstimateResponse  # noqa: E402
from front.streamlit.client.estimate_openai_client import (  # noqa: E402
    EstimateBackendError,
    EstimateOpenAIBackendClient,
    EstimateStreamEvent,
)

CHAT_MESSAGES_KEY = "estimate_chat_messages"
LAST_CALL_METRICS_KEY = "estimate_last_call_metrics"

PREDEFINED_PROMPT_TEXT = """
El cliente solicita una aplicación móvil para gestionar reservas de salas de reuniones en una empresa. La app debe permitir a los
empleados ver la disponibilidad, reservar, cancelar y recibir notificaciones. Se requiere autenticación corporativa, integración
con el calendario de Outlook y panel de administración web para métricas.
"""

ChatRole = Literal["user", "assistant"]


class ChatMessage(TypedDict):
    role: ChatRole
    content: str
    caption: str | None


class LastCallMetrics(TypedDict):
    model: str
    input_tokens: int
    output_tokens: int
    response_time_seconds: float


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
    if LAST_CALL_METRICS_KEY not in st.session_state:
        st.session_state[LAST_CALL_METRICS_KEY] = None


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


def build_stream_estimate_caption(event: EstimateStreamEvent) -> str:
    caption_parts = [
        f"Proveedor: {event.get('provider', 'openai')}",
        f"Modelo: {event.get('llm_model', 'desconocido')}",
    ]

    if event.get("num_tokens_total") is not None:
        caption_parts.append(f"Tokens: {event['num_tokens_total']}")

    return " · ".join(caption_parts)


def build_last_call_metrics(
    event: EstimateStreamEvent,
    response_time_seconds: float,
) -> LastCallMetrics:
    return {
        "model": event.get("llm_model", "desconocido"),
        "input_tokens": event.get("num_tokens_input", 0),
        "output_tokens": event.get("num_tokens_response", 0),
        "response_time_seconds": response_time_seconds,
    }


def stream_estimation(
    client: EstimateOpenAIBackendClient,
    transcription: str,
) -> tuple[str, str | None, LastCallMetrics | None]:
    caption: str | None = None
    metadata_event: EstimateStreamEvent | None = None

    def tokens():
        nonlocal caption, metadata_event

        for event in client.stream_estimate_from_transcript(transcription):
            if event.get("type") == "delta":
                yield event.get("content", "")
            elif event.get("type") == "metadata":
                metadata_event = event
                caption = build_stream_estimate_caption(event)

    start_time = time.perf_counter()
    estimation = st.write_stream(tokens)
    response_time_seconds = time.perf_counter() - start_time

    metrics = None
    if metadata_event is not None:
        metrics = build_last_call_metrics(metadata_event, response_time_seconds)

    if isinstance(estimation, str):
        return estimation, caption, metrics

    return "".join(str(part) for part in estimation), caption, metrics


def process_transcription(transcription: str, metrics_placeholder) -> None:
    normalized_transcription = transcription.strip()

    if not normalized_transcription:
        st.warning("La transcripción no puede estar vacía.")
        return

    append_message("user", normalized_transcription)
    render_message(st.session_state[CHAT_MESSAGES_KEY][-1])

    with st.chat_message("assistant"):
        try:
            estimation, caption, metrics = stream_estimation(
                estimate_client,
                normalized_transcription,
            )
            if metrics:
                st.session_state[LAST_CALL_METRICS_KEY] = metrics
        except EstimateBackendError as exc:
            estimation = str(exc)
            caption = None
            st.error(estimation)

        if caption:
            st.caption(caption)

    append_message("assistant", estimation, caption)
    render_last_call_metrics(metrics_placeholder)


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


def render_last_call_metrics(container) -> None:
    metrics = st.session_state.get(LAST_CALL_METRICS_KEY)

    with container.container():
        st.subheader("Última llamada")
        if not metrics:
            st.caption("Aún no se ha generado ninguna estimación.")
            return

        st.metric("Modelo", metrics["model"])
        st.metric("Tokens de entrada", metrics["input_tokens"])
        st.metric("Tokens de salida", metrics["output_tokens"])
        st.metric("Tiempo de respuesta", f"{metrics['response_time_seconds']:.2f} s")


# Function to display and handle sidebar interactions
def handle_sidebar():
    selected_transcription = None

    with st.sidebar:
        st.subheader("Sesión")
        if st.button("Limpiar conversación", use_container_width=True):
            st.session_state[CHAT_MESSAGES_KEY] = []
            st.session_state[LAST_CALL_METRICS_KEY] = None
            st.rerun()

        if st.button("Cargar prompt predefinido", use_container_width=True):
            selected_transcription = PREDEFINED_PROMPT_TEXT

        st.divider()
        st.subheader("System prompt activo")
        st.text_area(
            "System prompt",
            value=SYSTEM_PROMPT,
            height=160,
            disabled=True,
            label_visibility="collapsed",
        )

        st.subheader("Contexto estático inyectado")
        st.text_area(
            "Estimaciones de ejemplo",
            value=format_examples_for_prompt(BASIC_ESTIMATION_EXAMPLES),
            height=320,
            disabled=True,
            label_visibility="collapsed",
        )

        st.divider()
        metrics_placeholder = st.empty()
        render_last_call_metrics(metrics_placeholder)

    return selected_transcription, metrics_placeholder


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

sidebar_transcription, metrics_placeholder = handle_sidebar()

render_chat_history()

transcription = st.chat_input("Escribe o pega la transcripción de la reunión")

if sidebar_transcription:
    process_transcription(sidebar_transcription, metrics_placeholder)
elif transcription:
    process_transcription(transcription, metrics_placeholder)

with debug_placeholder.container():
    with st.expander("Check State"):
        st.write(st.session_state)
