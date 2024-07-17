"""
Main web application service. Serves the static frontend as well as
API routes for transcription, language model generation and text-to-speech.
"""

import json
from pathlib import Path

from modal import Mount, asgi_app

from .common import app
from .engine import GameEngine

static_path = Path(__file__).with_name("frontend").resolve()


@app.function(
    mounts=[Mount.from_local_dir(static_path, remote_path="/assets")],
    container_idle_timeout=300,
    timeout=600,
)
@asgi_app()
def web():
    from fastapi import FastAPI, Request
    from fastapi.responses import Response, StreamingResponse
    from fastapi.staticfiles import StaticFiles

    web_app = FastAPI()
    game_engine = GameEngine()

    @web_app.post("/start_game")
    async def transcribe(request: Request):
        # Take in request string for a game name and initializes the game engine.
        # Should return the initial state of the game
        body = await request.json()
        return result["text"]

    @web_app.post("/user_command")
    async def generate(request: Request):
        body = await request.json()

        # Can we return StreamingResponse here? Since the actual LLM-rewritten
        # response may take multiple trips and we may not know when it is ready
        # to return to the user until we have received the entire response.

        for segment in llm.generate.remote_gen(body["input"], body["history"]):
            yield {"type": "text", "value": segment}
            sentence += segment

        def gen_serialized():
            for i in gen():
                yield json.dumps(i) + "\x1e"

        return StreamingResponse(
            gen_serialized(),
            media_type="text/event-stream",
        )

    web_app.mount("/", StaticFiles(directory="/assets", html=True))
    return web_app
