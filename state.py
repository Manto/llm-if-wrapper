import os
import toml
from anthropic import Anthropic
import jericho
import uuid


class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.id = None  # specifying this game session, in uuid format
        self.debug_log = None  # open fd for a debug log file
        self.transcript_orig = None  # open fd for original game transcript
        self.transcript_llm = None  # open fd for llm enhanced transcript

        self.env = None  # the jericho Frotz environment
        self.tone = "original"  # One of "original", "pratchett", "gumshoe", "hardyboys", "spaceopera"
        self.game_chatlog = []  # the log of game inputs and outputs
        self.llm_chatlog = []  # the log of LLM inputs and outputs
        self.llm_prompt = ""  # the current LLM prompt being constructed


config = None
with open("./configs/config.toml", "r") as config_file:
    config = toml.load(config_file)

llm_config = None
with open("./configs/llm.toml", "r") as llm_config:
    llm_config = toml.load(llm_config)

llm_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

_current_state = GameState()


def init_game_state(tone=None):
    """
    TODO: save/load from Modal Dict
    """
    _current_state.reset()
    state_id = uuid.uuid4()
    _current_state.id = state_id

    game_path = config["init"]["game_path"]
    env = jericho.FrotzEnv(game_path)
    _current_state.env = env

    # TODO: Update this to use the state ID
    _current_state.debug_log = open("./logs/debug.log", "w")
    _current_state.transcript_orig = open("./logs/transscript_orig.log", "w")
    _current_state.transcript_llm = open("./logs/transscript_llm.log", "w")
    _current_state.tone = tone
    return _current_state


def get_current_state():
    return _current_state


def get_existing_state(id):
    return state_cache[id]
