import json
from pathlib import Path

import modal
import os
from common import app, vol
from llm_serve import LLM
import engine

static_path = os.path.join(os.getcwd(), "frontend", "out")
game_path = os.path.join(os.getcwd(), "games")
config_path = os.path.join(os.getcwd(), "configs")


@app.function(
    mounts=[
        modal.Mount.from_local_dir(static_path, remote_path="/assets"),
        modal.Mount.from_local_dir(config_path, remote_path="/root/configs"),
        modal.Mount.from_local_dir(game_path, remote_path="/root/games"),
    ],
    volumes={"/root/logs": vol},
    _allow_background_volume_commits=True,
    secrets=[modal.Secret.from_dotenv()],
    container_idle_timeout=300,
    timeout=600,
)
@modal.asgi_app()
def web():
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import Response, StreamingResponse
    from fastapi.staticfiles import StaticFiles
    import engine
    import state

    web_app = FastAPI()
    llm = LLM()
    web_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["POST", "GET"],
        allow_headers=["*"],
        max_age=3600,
    )

    @web_app.post("/start_game")
    async def start_game(request: Request):
        # Take in request string for a game name and initializes the game engine.
        # Should return the initial state of the game
        body = await request.json()
        game_path = f"games/{body['game_id']}"
        llm_provider = body["llm_provider"]
        tone = body.get("tone")

        new_state = state.init_game_state(
            game_path, llm_provider, tone, id_in_log_path=True
        )
        state.set_current_state(new_state)

        input_command, game_command, game_response, llm_response, is_game_over = (
            engine.start_new_game()
        )

        state.save_state(new_state)

        return {
            "id": new_state.id,
            "input_command": input_command,
            "game_command": game_command,
            "game_response": game_response,
            "llm_response": llm_response,
            "is_game_over": is_game_over,
        }

    @web_app.post("/user_command")
    async def user_command(request: Request):
        body = await request.json()
        game_id = body["game_id"]
        input_command = body["input"]

        loaded_state = state.load_state_by_id(game_id)
        state.set_current_state(loaded_state)

        input_command, game_command, game_response, llm_response, is_game_over = (
            engine.process_input(input_command)
        )

        state.save_state(loaded_state)

        return {
            "id": loaded_state.id,
            "input_command": input_command,
            "game_command": game_command,
            "game_response": game_response,
            "llm_response": llm_response,
            "is_game_over": is_game_over,
        }

    @web_app.post("/warm_inference")
    def warm_inference(request: Request):
        llm.warm_up.remote_gen()
        return "Done"

    @web_app.post("/inference")
    async def inference(request: Request):
        body = await request.json()
        system_msg = body.get("system", "You are a helpful assistant.")
        user_msg = body.get("user")

        if not user_msg:
            raise HTTPException(status_code=400, detail="No user message.")

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]

        def _gen(msgs):
            for segment in llm.completion_stream.remote_gen(msgs):
                yield segment

        return StreamingResponse(
            _gen(messages),
            media_type="text/event-stream",
        )

    web_app.mount("/", StaticFiles(directory="/assets", html=True))
    web_app.mount("/logs", StaticFiles(directory="/root/logs"))
    return web_app
