import asyncio

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

chat_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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
