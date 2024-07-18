import fcntl
import jericho
import hashlib
import modal
import os
import re
import requests
import sys
import time

from splitscreen import SplitScreen

from game import (
    add_to_game_log,
    try_to_fix_parser_error,
    is_parser_error,
    add_recent_gamelog_and_visited_rooms_to_llm_prompt,
)
from utils import (
    write_to_debug_log,
    concat_current_llm_prompt,
    get_llm_response,
)
from state import (
    config,
    get_current_state,
)


def init_rewrites(game_init_text):
    """
    Performs first rewrite of the initial game response
    """
    state = get_current_state()
    concat_current_llm_prompt(config["style"]["tone_" + state.tone])
    concat_current_llm_prompt(config["style"]["length"])
    concat_current_llm_prompt(config["style"]["formatting"])
    concat_current_llm_prompt(config["style"]["caveat"])
    concat_current_llm_prompt(config["init"]["startup"])

    if game_init_text[-1] == ">":  # remove input prompt, if there
        game_init_text = game_init_text[:-1]
        game_init_text = game_init_text.rstrip()
    concat_current_llm_prompt(game_init_text)
    return get_llm_response()


def rewrite_response(command, response):
    """
    Rewriting game response after given an user command.
    User command should have gone through parser error check.
    """
    input = False
    if not response:
        return response

    if response[-1] == ">":  # remove input prompt, if there
        response = response[:-1]
        input = True
    command = command.strip()
    response = response.strip()

    state = get_current_state()
    concat_current_llm_prompt(config["style"]["tone_" + state.tone])
    concat_current_llm_prompt(config["style"]["length"])
    concat_current_llm_prompt(config["style"]["formatting"])
    concat_current_llm_prompt(config["style"]["caveat"])
    add_recent_gamelog_and_visited_rooms_to_llm_prompt()

    # We should have tried to fix parser error by this point.
    # If we're at an unfixable error, just make stuff up
    if is_parser_error(response):
        concat_current_llm_prompt(config["errors"]["generic"])

    # Perform LLM rewrite.
    template = config["responses"]["generic"]
    prompt = template.replace("{{{command}}}", command).replace(
        "{{{response}}}", response
    )
    concat_current_llm_prompt(prompt)
    concat_current_llm_prompt(config["responses"]["suffix"])
    llm_response = get_llm_response()

    if input == True:
        llm_response = llm_response + "\n\n>"
    return llm_response


def start_new_game():
    state = get_current_state()

    # Initial response, rewritten with LLM
    game_response, info = state.env.reset()
    add_to_game_log(game_response, is_command=False)

    if state.tone == "none":
        llm_response = game_response
    else:
        llm_response = init_rewrites(game_response)

    return None, None, game_response, llm_response, False


def process_input(input_command):
    state = get_current_state()

    write_to_debug_log(f"=== User Input ===\n{input_command}\n\n")

    temp_game_state = state.env.get_state()
    game_response, _, is_game_over, ___ = state.env.step(input_command)

    write_to_debug_log(f"=== Game Response ===\n{game_response}\n\n")

    # If we detected parse error, try LLM rewrite
    if is_parser_error(game_response):
        write_to_debug_log("UNRECOGNIZED COMMAND: " + input_command + "\n\n")

        # First, we roll back to the state before error, just in case
        # the failed command changes game state.
        state.env.set_state(temp_game_state)

        game_command = try_to_fix_parser_error(input_command, game_response)
        write_to_debug_log(f"=== Alt. User Input ===\n{game_command}\n\n")

        game_response, _, is_game_over, ___ = state.env.step(game_command)
        write_to_debug_log(f"=== Alt. Game Response===\n{game_response}\n\n")
    else:
        game_command = input_command

    # Finally, perform LLM rewrite for the game response
    # Note that we're writing with the original user input
    if state.tone == "none":
        llm_response = game_response
    else:
        llm_response = rewrite_response(input_command, game_response)

    add_to_game_log(game_command, is_command=True)
    add_to_game_log(game_response, is_command=False)

    return input_command, game_command, game_response, llm_response, is_game_over
