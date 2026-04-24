import logging
import time
from collections.abc import AsyncIterator
from typing import Any

from langchain_core.messages import HumanMessage

from app.services.agent.agent_provider import ChatAgentProvider
from app.services.agent.timeout_policy import StreamTimeoutPolicy

logger = logging.getLogger(__name__)


class ChatStreamProducer:
    def __init__(self, user, 
                agent_provider: ChatAgentProvider,
                timeout_policy: StreamTimeoutPolicy):
        self.user = user
        self.timeout_policy = timeout_policy
        self.agent_provider = agent_provider

    async def produce(
        self, checkpointer, chat_id: int, human_message: HumanMessage
    ) -> AsyncIterator[tuple[str, Any]]:
        agent = self.agent_provider.build(checkpointer)

        last_event_at = time.monotonic()

        try:
            async for chunk in agent.astream(
                {"messages": [human_message], "user_id": self.user.id, "chat_id": chat_id},
                stream_mode="messages",
                config={"configurable": {"thread_id": chat_id}},
            ):
                last_event_at = time.monotonic()
                yield "chunk", chunk
        except Exception:
            logger.exception("Chat stream failed", extra={"chat_id": chat_id})
            yield "error", None
            return

        if self.timeout_policy.has_timed_out(last_event_at):
            yield "timeout", None
            return

        yield "done", None
