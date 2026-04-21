import asyncio

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from app.db_agent import CheckpointerDep
from app.services.agent.agent import make_graph

chat_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Message(BaseModel):
    message: str


class ChatRequest(BaseModel):
    message: str


@chat_router.post("/chat")
async def chat(request: ChatRequest):
    respuestas = {
        "hola": "Hola! En qué te puedo ayudar hoy? ",
        "lunes": "Para el lunes te sugiero unos tacos de pollo. ",
        "martes": "Para el martes qué tal una sopa de verduras. ",
    }

    texto = respuestas.get(request.message.lower(), "No entendí tu mensaje. ")

    async def event_generator():

        for palabra in texto.split(" "):
            await asyncio.sleep(0.3)
            yield f"data: {palabra} \n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@chat_router.post("/chat/{chat_id}/stream")
async def stream_chat(chat_id: int, message: Message, checkpointer: CheckpointerDep):
    human_message = HumanMessage(content=message.message)
    agent = make_graph(config={"checkpointer": checkpointer})

    def generate_response():
        for chunk in agent.stream(
            {"messages": [human_message], "user_id": 1, "chat_id": chat_id},
            stream_mode="messages",
            config={"configurable": {"thread_id": chat_id}},
        ):
            node, _ = chunk
            yield f"data: {node.content}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
