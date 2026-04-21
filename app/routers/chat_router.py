import json
import logging
import os
import queue
import threading
import time

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from app.db_agent import CheckpointerDep
from app.services.agent.agent import make_graph

chat_router = APIRouter()
logger = logging.getLogger(__name__)
STREAM_IDLE_TIMEOUT_SECONDS = int(os.getenv("CHAT_STREAM_IDLE_TIMEOUT_SECONDS", "30"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Message(BaseModel):
    message: str


class ChatRequest(BaseModel):
    message: str


def _sse_data(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@chat_router.post("/chat/{chat_id}/stream")
async def stream_chat(chat_id: int, message: Message, checkpointer: CheckpointerDep):
    if not message.message.strip():
        raise HTTPException(status_code=422, detail="Message cannot be empty.")

    if checkpointer is None:
        raise HTTPException(status_code=503, detail="Checkpointer is not available.")

    human_message = HumanMessage(content=message.message)
    agent = make_graph(config={"checkpointer": checkpointer})
    logger.info("Starting chat stream", extra={"chat_id": chat_id})

    def generate_response():
        sequence = 0
        events: queue.Queue = queue.Queue()

        def worker() -> None:
            try:
                for chunk in agent.stream(
                    {"messages": [human_message], "user_id": 1, "chat_id": chat_id},
                    stream_mode="messages",
                    config={"configurable": {"thread_id": chat_id}},
                ):
                    events.put(("chunk", chunk))

                events.put(("done", None))
            except Exception:
                logger.exception("Chat stream worker failed", extra={"chat_id": chat_id})
                events.put(("error", None))

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        last_event_at = time.monotonic()

        try:
            while True:
                try:
                    kind, payload = events.get(timeout=1)
                    last_event_at = time.monotonic()
                except queue.Empty:
                    if time.monotonic() - last_event_at > STREAM_IDLE_TIMEOUT_SECONDS:
                        logger.warning(
                            "Chat stream timed out due to inactivity",
                            extra={
                                "chat_id": chat_id,
                                "timeout_seconds": STREAM_IDLE_TIMEOUT_SECONDS,
                            },
                        )
                        yield _sse_data(
                            {
                                "type": "error",
                                "chat_id": chat_id,
                                "message": "Chat stream timed out.",
                            }
                        )
                        return

                    continue

                if kind == "chunk":
                    try:
                        node = payload[0] if isinstance(payload, tuple) else payload
                        content = getattr(node, "content", None)

                        if not content:
                            continue

                        sequence += 1
                        logger.debug(
                            "Streaming chat chunk",
                            extra={"chat_id": chat_id, "sequence": sequence},
                        )
                        yield _sse_data(
                            {
                                "type": "message",
                                "chat_id": chat_id,
                                "sequence": sequence,
                                "content": content,
                            }
                        )
                    except Exception:
                        logger.exception(
                            "Failed while processing chat chunk", extra={"chat_id": chat_id}
                        )
                        yield _sse_data(
                            {
                                "type": "error",
                                "chat_id": chat_id,
                                "message": "Failed while processing response chunk.",
                            }
                        )
                        return

                elif kind == "done":
                    yield _sse_data({"type": "done", "chat_id": chat_id})
                    return

                elif kind == "error":
                    yield _sse_data(
                        {
                            "type": "error",
                            "chat_id": chat_id,
                            "message": "Chat stream failed.",
                        }
                    )
                    return
        except Exception:
            logger.exception("Chat stream failed", extra={"chat_id": chat_id})
            yield _sse_data(
                {
                    "type": "error",
                    "chat_id": chat_id,
                    "message": "Chat stream failed.",
                }
            )
            return

    try:
        return StreamingResponse(
            generate_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )
    except Exception as err:
        logger.exception("Failed to start chat stream", extra={"chat_id": chat_id})
        raise HTTPException(status_code=500, detail="Could not start chat stream.") from err
