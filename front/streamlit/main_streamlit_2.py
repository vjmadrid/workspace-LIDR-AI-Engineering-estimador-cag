import sys
from pathlib import Path
from typing import Literal, TypedDict

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import get_settings  # noqa: E402
from app.response.estimate_responses import EstimateResponse  # noqa: E402
from front.streamlit.client.estimate_client import (  # noqa: E402
    EstimateBackendClient,
    EstimateBackendError,
)

CHAT_MESSAGES_KEY = "estimate_chat_messages"

ChatRole = Literal["user", "assistant"]


class ChatMessage(TypedDict):
    role: ChatRole
    content: str
    caption: str | None


@st.cache_resource
def get_estimate_client(
    base_url: str,
    timeout_seconds: float,
) -> EstimateBackendClient:
    return EstimateBackendClient(
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
    st.session_state[CHAT_MESSAGES_KEY].append(message)


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
    client: EstimateBackendClient,
    transcription: str,
) -> tuple[str, str]:
    response = client.estimate_from_transcript(transcription)
    return response.estimation, build_estimate_caption(response)


st.set_page_config(
    page_title="Estimador CAG",
    page_icon="💬",
)

settings = get_settings()
client = get_estimate_client(
    settings.ESTIMATE_BACKEND_BASE_URL,
    settings.ESTIMATE_BACKEND_TIMEOUT_SECONDS,
)

initialize_chat_state()

st.title("Estimador CAG")
st.caption("Pega una transcripción de reunión y recibirás una estimación de software generada por el backend del proyecto.")

with st.sidebar:
    st.subheader("Sesión")
    if st.button("Limpiar conversación", use_container_width=True):
        st.session_state[CHAT_MESSAGES_KEY] = []
        st.rerun()

render_chat_history()

transcription = st.chat_input("Escribe o pega la transcripción de la reunión")

if transcription:
    normalized_transcription = transcription.strip()
    if not normalized_transcription:
        st.warning("La transcripción no puede estar vacía.")
    else:
        append_message("user", normalized_transcription)
        render_message(st.session_state[CHAT_MESSAGES_KEY][-1])

        with st.chat_message("assistant"):
            with st.spinner("Generando estimación..."):
                try:
                    estimation, caption = request_estimation(
                        client,
                        normalized_transcription,
                    )
                except EstimateBackendError as exc:
                    estimation = str(exc)
                    caption = None

            st.markdown(estimation)
            if caption:
                st.caption(caption)

        append_message("assistant", estimation, caption)
