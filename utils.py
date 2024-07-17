# Utility functions

import io
import logging
import textwrap
from state import get_current_state, llm_client, llm_config, config


def format_with_linebreaks(text: str, width: int) -> str:
    lines = []
    for line in text.split("\n"):
        if len(line) > width - 1:
            line = textwrap.fill(line, width=width)
        lines.append(line)
    return "\n".join(lines)


def write_to_debug_log(output):
    state = get_current_state()
    if state.debug_log != None:
        state.debug_log.write(output)
        state.debug_log.flush()


def write_to_transcript(output):
    state = get_current_state()
    if state.transcript:
        state.transcript.write(output)
        state.transcript.flush()


def get_file_text(filename: str, regexp: str) -> str:
    if os.path.isfile(filename):
        with open(filename, "r") as file:
            text = file.read()
        match = re.search(regexp, text, re.DOTALL)
        if match:
            result = match.group(1)
            return regexp.replace("(.*)", result)
        else:
            logging.warn(f"Regexp {regexp} not matched in file '{filename}'")
    else:
        logging.warn(f"File {filename} not found as background info.")
    return ""


def get_llm_response(trial=False):
    """
    Sends out the current LLM prompt being built then return response

    TODO: Something odd about not sending previous chat sequences to LLM
    Will take more token but should improve consistency.

    Args:
        trial: if True, don't add the prompt to the chatlog
    """

    state = get_current_state()
    prompt = {"role": "user", "content": state.llm_prompt}
    if not trial:
        state.llm_chatlog.append(prompt)

    # make a request with the prompt
    resp = llm_client.messages.create(
        model=llm_config["config"]["name"],
        system=config["init"]["llm_init"],
        max_tokens=llm_config["config"]["max_tokens"],
        messages=[prompt],
        temperature=llm_config["config"]["temp"],
    )
    tokens = resp.usage.input_tokens
    response = resp.content[0].text

    write_to_debug_log(f"===LLM RESPONSE in {tokens} tokens===\n")
    write_to_debug_log(response + "\n\n")

    message = {"role": "assistant", "content": response}
    if not trial:
        state.llm_chatlog.append(message)

    # reset the current LLM prompt
    state.llm_prompt = ""
    return response


def concat_current_llm_prompt(prompt):
    state = get_current_state()
    if not prompt[-1] == ">":
        state.llm_prompt = state.llm_prompt + "\n"

    state.llm_prompt = state.llm_prompt + prompt
    return
