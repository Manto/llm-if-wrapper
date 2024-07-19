import os
import toml
import modal
import jericho
import uuid


class GameState:
    def __init__(self):
        self.id = None  # specifying this game session, in uuid format
        self.debug_log = None  # open fd for a debug log file

        self.env = None  # the jericho Frotz environment
        self.game_path = ""
        self.tone = (
            None  # One of "original", "pratchett", "gumshoe", "zen", "spaceopera"
        )
        self.llm_provider = ""  # Supports "anthropic" or "hosted"

        self.game_chatlog = []  # the log of game inputs and outputs
        self.llm_prompt = ""  # the current LLM prompt being constructed


config = None
with open("configs/config.toml", "r") as config_file:
    config = toml.load(config_file)

llm_config = None
with open("configs/llm.toml", "r") as llm_config:
    llm_config = toml.load(llm_config)

# NOTE: A bit of a hack to quickly enable both web and local execution
_current_state = None


def get_current_state():
    global _current_state
    return _current_state


def set_current_state(state):
    global _current_state
    _current_state = state


def init_game_state(game_path, llm_provider, tone=None, id_in_log_path=False):
    """
    TODO: save/load from Modal Dict
    """
    state = GameState()
    state_id = str(uuid.uuid4())
    state.id = state_id
    state.game_path = game_path
    state.llm_provider = llm_provider
    state.tone = tone

    env = jericho.FrotzEnv(game_path)
    state.env = env

    # TODO: Update this to use the state ID
    debug_path = f"logs/debug{'-' + state_id if id_in_log_path else ''}.log"
    state.debug_log = open(debug_path, "w")
    return state


def save_state(state):
    """
    Used by Modal web endpoint to persist game state in between requests.
    """
    state_dict = modal.Dict.from_name(
        f"llm-text-adv-{state.id}", create_if_missing=True
    )

    state_dict["id"] = state.id
    state_dict["game_path"] = state.game_path
    state_dict["llm_provider"] = state.llm_provider
    state_dict["tone"] = state.tone

    state_dict["game_chatlog"] = state.game_chatlog
    state_dict["game_state"] = state.env.get_state()


def load_state_by_id(id):
    """
    Used by Modal web endpoint to restore existing game state in between requests.
    """
    state_dict = modal.Dict.from_name(f"llm-text-adv-{id}", create_if_missing=False)
    if not state_dict:
        raise Exception(f"Unable to load state for {id}")

    loaded_state = GameState()
    loaded_state.id = id
    loaded_state.game_path = state_dict["game_path"]
    loaded_state.llm_provider = state_dict["llm_provider"]
    loaded_state.tone = state_dict["tone"]

    loaded_state.game_chatlog = state_dict["game_chatlog"]
    loaded_state.llm_prompt = ""

    env = jericho.FrotzEnv(state_dict["game_path"])
    env.set_state(state_dict["game_state"])
    loaded_state.env = env

    debug_path = f"logs/debug-{id}.log"
    loaded_state.debug_log = open(debug_path, "w")

    return loaded_state
