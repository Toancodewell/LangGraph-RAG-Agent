from app.config import settings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent

from .prompts import SYSTEM_PROMPT
from .tools import tools


def create_model(model_name: str, streaming: bool = False) -> BaseChatModel:
    """Create a retrieval chain based on the provided model name."""

    model = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=settings.api_key.get_secret_value(),
        disable_streaming=not streaming,
    )

    return model


def build_retrival_graph(checkpointer: BaseCheckpointSaver, model_name: str) -> CompiledStateGraph:
    """Build a retrieval chain based on the provided model name."""

    model = create_model(model_name=model_name)
    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )

    return agent
