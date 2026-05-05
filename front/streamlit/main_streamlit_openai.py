import sys
from pathlib import Path
from typing import Literal, TypedDict

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import get_settings  # noqa: E402
from app.response.estimate_responses import EstimateResponse  # noqa: E402
from front.streamlit.client.estimate_openai_client import (  # noqa: E402
    EstimateBackendError,
    EstimateOpenAIBackendClient,
)

CHAT_MESSAGES_KEY = "estimate_chat_messages"

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


def request_estimation(
    client: EstimateOpenAIBackendClient,
    transcription: str,
) -> tuple[str, str]:
    response = client.estimate_from_transcript(transcription)
    return response.estimation, build_estimate_caption(response)


def process_transcription(transcription: str) -> None:
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
    with st.sidebar:
        st.subheader("Sesión")
        if st.button("Limpiar conversación", use_container_width=True):
            st.session_state[CHAT_MESSAGES_KEY] = []
            st.rerun()

        if st.button("Cargar prompt predefinido", use_container_width=True):
            return PREDEFINED_PROMPT_TEXT

    return None

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

sidebar_transcription = handle_sidebar()

render_chat_history()

transcription = st.chat_input("Escribe o pega la transcripción de la reunión")

if sidebar_transcription:
    process_transcription(sidebar_transcription)
elif transcription:
    process_transcription(transcription)

with debug_placeholder.container():
    with st.expander("Check State"):
        st.write(st.session_state)
