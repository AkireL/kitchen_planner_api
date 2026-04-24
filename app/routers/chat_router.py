from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.db_agent import CheckpointerDep
from app.models import User
from app.services.agent.agent_provider import ChatAgentProvider
from app.services.agent.chat_stream_service import ChatStreamService
from app.services.agent.event_formatter import ChatEventFormatter
from app.services.agent.producer import ChatStreamProducer
from app.services.agent.timeout_policy import StreamTimeoutPolicy
from app.services.auth_service import AuthService

chat_router = APIRouter(dependencies=[Depends(AuthService.get_current_user)])


class Message(BaseModel):
    message: str


class ChatRequest(BaseModel):
    message: str


@chat_router.post("/chat/{chat_id}/stream")
async def stream_chat(
    user: Annotated[User, Depends(AuthService.get_current_user)],
    chat_id: int,
    message: Message,
    checkpointer: CheckpointerDep,
):
    timeout_policy = StreamTimeoutPolicy()
    producer = ChatStreamProducer(user, ChatAgentProvider(), timeout_policy)
    stream_service = ChatStreamService(user, producer, ChatEventFormatter())

    return StreamingResponse(
        stream_service.stream(chat_id, message.message, checkpointer),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
