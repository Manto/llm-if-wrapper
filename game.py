import re
import jericho
import sys

from state import get_current_state, config
from utils import (
    write_to_debug_log,
    concat_current_llm_prompt,
    get_llm_response,
)


def is_parser_error(response):
    """
    Check if the response is a parser error
    Returns True if it is, False otherwise
    """
    # Use Jericho's logic to determine if the response is a parser error
    if not jericho.util.recognized(response):
        return True

    # Then use the list of regex provided by config
    for prefix in config["errors"]["prefixes"]:
        if response.startswith(prefix):
            return True
    return False


def add_recent_gamelog_and_current_room_to_llm_prompt():
    state = get_current_state()
    current_room, gamelog = get_current_room_and_gamelog()
    gamelog_text = config["responses"]["gamelog"].replace("{{{gamelog}}}", gamelog)
    concat_current_llm_prompt(gamelog_text)

    current_room = config["responses"]["current_room"].replace(
        "{{{current_room}}}", current_room
    )
    concat_current_llm_prompt(current_room)


def try_to_fix_parser_error(command, response):
    """
    Given a user command and the parser error response, use the LLM to
    come up with a command that generates reasonable result.

    Returns the new command to try, or the original command if no fix is found.
    """
    state = get_current_state()

    # get all the verbs for the game, and all the nouns accessible in the current room
    verbs = [w for w in state.env.get_dictionary() if w.is_verb]
    verbs = ", ".join([f'"{v.word}"' for v in verbs])
    nouns = [w for w in state.env.get_dictionary() if w.is_noun]
    nouns = ", ".join([f'"{n.word}"' for n in nouns])

    # try several times to get the LLM to make a command that doesn't result in an parser error
    preamble = config["errors"]["parser_preamble"].replace("{{{verbs}}}", verbs)
    preamble = preamble.replace("{{{nouns}}}", nouns)

    possible_actions = "\n".join(state.env.get_valid_actions())
    possible_actions = config["errors"]["parser_rewrite_possible_actions"].replace(
        "{{{possible_actions}}}", possible_actions
    )

    error_response = config["responses"]["generic"].replace("{{{command}}}", command)
    error_response = error_response.replace("{{{response}}}", response)
    tries = []
    new_command = command

    for i in range(config["errors"]["retries"]):
        # Save current game state so we can roll back after
        # trying alternative commands
        temp_game_state = state.env.get_state()

        add_recent_gamelog_and_current_room_to_llm_prompt()
        concat_current_llm_prompt(error_response)
        concat_current_llm_prompt(preamble)
        concat_current_llm_prompt(possible_actions)

        if len(tries) > 0:
            failed_tries_prompt = "\n".join(tries)
            failed_tries_prompt = config["errors"]["parser_rewrite_tries"].replace(
                "{{{alternative_commands}}}", failed_tries_prompt
            )
            concat_current_llm_prompt(failed_tries_prompt)
        concat_current_llm_prompt(config["errors"]["parser_suffix"])

        llm_response = get_llm_response()

        # Attempt to parse out the newly suggested command
        # If we can't find a suggested command, we give up and return original
        new_command = re.findall("\\+\\+\\+(.*?)\\+\\+\\+", llm_response)
        if new_command == []:
            break

        new_command = new_command[0]
        write_to_debug_log(f"LLM COMMAND REWRITING SUGGESTION:\n{new_command}\n\n")
        new_response, _, __, ___ = state.env.step(new_command)
        write_to_debug_log(f"LLM COMMAND REWRITING RESPONSE:\n{new_response}\n\n")

        # Restore game state after testing new command
        state.env.set_state(temp_game_state)

        # Once we get a good command, use that to resume the game loop
        if not is_parser_error(new_response):
            command = new_command
            break

        tries.append(new_command)

    return command


def add_to_game_log(output, is_command=False):
    """
    Maintain a playlog of the original game, as it is played
    """
    state = get_current_state()

    if not output:
        return

    if is_command:
        output = f"{config['responses']['command_prefix']} {output}"
    if output.rstrip()[-1] == ">":  # remove input prompt, if there
        output = output.rstrip()[:-1]
        output = output.rstrip() + "\n"
    state.game_chatlog.append([is_command, output])


def get_current_room_and_gamelog():
    """
    Get the most recent part of the game playlog as well as
    the CURRENT room (a deviation from original implementation)
    """
    state = get_current_state()

    gamelog_count = config["responses"]["gamelog_count"]
    if gamelog_count == 0:
        gamelog_count = len(state.game_chatlog)
    else:
        gamelog_count = 2 * gamelog_count
    gamelog = state.game_chatlog[-gamelog_count:]
    gamelog_text = "\n".join([text for [b, text] in gamelog])

    # Use a normal look command to get current room info.
    # We still save/restore state just in case looking changes the game.
    backup_state = state.env.get_state()
    current_room, _, _, _ = state.env.step("look")
    state.env.set_state(backup_state)

    return current_room, gamelog_text
