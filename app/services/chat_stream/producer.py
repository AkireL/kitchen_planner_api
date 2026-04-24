import logging
import queue
import threading
import time
from collections.abc import Iterator
from typing import Any

from langchain_core.messages import HumanMessage

from app.services.chat_stream.agent_provider import ChatAgentProvider
from app.services.chat_stream.timeout_policy import StreamTimeoutPolicy

logger = logging.getLogger(__name__)


class ChatStreamProducer:
    def __init__(self, user, 
                agent_provider: ChatAgentProvider,
                timeout_policy: StreamTimeoutPolicy):
        self.user = user
        self.timeout_policy = timeout_policy
        self.agent_provider = agent_provider

    def produce(
        self, checkpointer, chat_id: int, human_message: HumanMessage
    ) -> Iterator[tuple[str, Any]]:
        events: queue.Queue = queue.Queue()
        agent = self.agent_provider.build(checkpointer)

        def worker() -> None:
            try:
                for chunk in agent.stream(
                    {"messages": [human_message], "user_id": self.user.id, "chat_id": chat_id},
                    stream_mode="messages",
                    config={"configurable": {"thread_id": chat_id}},
                ):
                    events.put(("chunk", chunk))

                events.put(("done", None))
            except Exception:
                logger.exception("Chat stream worker failed", extra={"chat_id": chat_id})
                events.put(("error", None))

        threading.Thread(target=worker, daemon=True).start()

        last_event_at = time.monotonic()

        while True:
            try:
                kind, payload = events.get(timeout=1)
                last_event_at = time.monotonic()
                yield kind, payload
            except queue.Empty:
                if self.timeout_policy.has_timed_out(last_event_at):
                    yield "timeout", None
                    return
