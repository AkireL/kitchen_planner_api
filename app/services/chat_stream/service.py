import logging
from collections.abc import Iterator

from fastapi import HTTPException
from langchain_core.messages import HumanMessage

from app.services.chat_stream.event_formatter import ChatEventFormatter
from app.services.chat_stream.producer import ChatStreamProducer

logger = logging.getLogger(__name__)


class ChatStreamService:
    def __init__(
        self,
        producer: ChatStreamProducer,
        formatter: ChatEventFormatter,
    ):
        self.producer = producer
        self.formatter = formatter

    def stream(self, chat_id: int, message_text: str, checkpointer) -> Iterator[str]:
        self._validate_stream_input(message_text, checkpointer)

        human_message = HumanMessage(content=message_text)
        logger.info("Starting chat stream", extra={"chat_id": chat_id})

        def generate_response():
            sequence = 0

            try:
                for kind, payload in self.producer.produce(checkpointer, chat_id, human_message):
                    if kind == "chunk":
                        node = payload[0] if isinstance(payload, tuple) else payload
                        content = getattr(node, "content", None)

                        if not content:
                            continue

                        sequence += 1
                        logger.debug(
                            "Streaming chat chunk", extra={"chat_id": chat_id, "sequence": sequence}
                        )
                        yield self.formatter.sse(
                            {
                                "type": "message",
                                "chat_id": chat_id,
                                "sequence": sequence,
                                "content": content,
                            }
                        )
                    elif kind == "done":
                        yield self.formatter.sse({"type": "done", "chat_id": chat_id})
                        return
                    elif kind == "timeout":
                        idle_timeout_seconds = self.producer.timeout_policy.idle_timeout_seconds

                        logger.warning(
                            "Chat stream timed out due to inactivity",
                            extra={
                                "chat_id": chat_id,
                                "timeout_seconds": idle_timeout_seconds,
                            },
                        )
                        yield self.formatter.sse(
                            {
                                "type": "error",
                                "chat_id": chat_id,
                                "message": "Chat stream timed out.",
                            }
                        )
                        return
                    elif kind == "error":
                        yield self.formatter.sse(
                            {"type": "error", "chat_id": chat_id, "message": "Chat stream failed."}
                        )
                        return
            except Exception:
                logger.exception("Chat stream failed", extra={"chat_id": chat_id})
                yield self.formatter.sse(
                    {"type": "error", "chat_id": chat_id, "message": "Chat stream failed."}
                )

        return generate_response()

    @staticmethod
    def _validate_stream_input(message_text: str, checkpointer) -> None:
        if not message_text.strip():
            raise HTTPException(status_code=422, detail="Message cannot be empty.")

        if checkpointer is None:
            raise HTTPException(status_code=503, detail="Checkpointer is not available.")
