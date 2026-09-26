import json
from typing import Any, AsyncGenerator, AsyncIterable

from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, AIMessageChunk, ToolMessage
from loguru import logger
from pydantic import BaseModel


def content_to_text(content: Any) -> str:
    """Extract plain text from a message content that may be a string or a list of
    content blocks (langchain-core 1.x returns list-of-blocks for Gemini 3.x)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("text"):
                parts.append(block["text"])
        return "".join(parts)
    return str(content) if content else ""


class PromptInput(BaseModel):
    prompt: str
    model_name: str


class Message(BaseModel):
    role: str
    content: str


class ChatStreamResponse(StreamingResponse):
    """
    It processes the LangGraph stream in different stream modes ("updates", "messages") and formats the data
    into JSON objects before sending them to the client.
    """

    def __init__(self, astream: AsyncIterable[dict[str, Any | Any]], **kwargs):
        super().__init__(content=self.process_stream(astream), **kwargs)

    async def process_stream(self, astream: AsyncIterable[dict[str, Any | Any]]) -> AsyncGenerator[str, Any]:
        async for stream_mode, chunk in astream:
            if stream_mode == "messages":
                yield self._handle_messages_stream(chunk)  # type: ignore

            elif stream_mode == "updates":
                async for formatted_chunk in self._handle_updates_stream(chunk):  # type: ignore
                    yield formatted_chunk

    def _handle_messages_stream(self, chunk: tuple[AIMessageChunk | AIMessage, Any]) -> str:
        message = chunk[0]
        if isinstance(message, (AIMessageChunk, AIMessage)) and message.content:
            text = content_to_text(message.content)
            if not text:
                return ""
            response = {"type": "llm_chunk", "content": text}
            return json.dumps(response) + "\n"
        return ""

    async def _handle_updates_stream(self, chunk: dict[str, Any]) -> AsyncGenerator[str, Any]:
        for node_output in chunk.values():
            if "messages" not in node_output:
                continue

            message = node_output["messages"][-1]

            if isinstance(message, AIMessage):
                if message.tool_calls:
                    for tool_call in message.tool_calls:
                        response = {"type": "tool_call", "name": tool_call["name"], "args": tool_call["args"]}
                        yield json.dumps(response) + "\n"

            elif isinstance(message, ToolMessage):
                response = {"type": "tool_result", "name": message.name, "content": content_to_text(message.content)}
                yield json.dumps(response) + "\n"

            else:
                response = {"type": message.type, "content": content_to_text(message.content)}
                logger.debug(f"Unknown message type: {message.type} - {json.dumps(response)}")
