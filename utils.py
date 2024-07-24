import io
import textwrap
import os
from anthropic import Anthropic
from openai import OpenAI
from state import get_current_state, llm_config, config
from llm_serve import LLM

ANTHROPIC_MODEL = "claude-3-5-sonnet-20240620"
OPENAI_MODEL = "gpt-4o-mini"


def format_with_linebreaks(text: str, width: int) -> str:
    lines = []
    for line in text.split("\n"):
        if len(line) > width - 1:
            line = textwrap.fill(line, width=width)
        lines.append(line)
    return "\n".join(lines)


def write_to_debug_log(output):
    state = get_current_state()
    if state.debug_path:
        with open(state.debug_path, "a+") as f:
            f.write(output)

        if state.post_debug_log_write:
            state.post_debug_log_write()


def get_llm_response_for_current_prompt():
    """
    Sends out the current LLM prompt being built then return response

    TODO: Do we want to send previous game log for more consistency?
    """
    state = get_current_state()
    response = make_llm_inference(config["init"]["system_prompt"], state.llm_prompt)
    # reset the current LLM prompt
    state.llm_prompt = ""

    return response


def make_llm_inference(system_prompt, user_prompt):

    state = get_current_state()
    write_to_debug_log(f"=== LLM REQUEST ({state.llm_provider}) ===\n")
    write_to_debug_log(user_prompt + "\n\n")

    prompt = {"role": "user", "content": user_prompt}

    if state.llm_provider == "anthropic":
        llm_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        resp = llm_client.messages.create(
            model=ANTHROPIC_MODEL,
            system=system_prompt,
            max_tokens=llm_config["config"]["max_tokens"],
            messages=[prompt],
            temperature=llm_config["config"]["temp"],
        )
        response = resp.content[0].text
    elif state.llm_provider == "openai":
        llm_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        completion = llm_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                prompt,
            ],
        )
        response = completion.choices[0].message.content
    elif state.llm_provider == "hosted":
        llm = LLM()
        response = ""
        for segment in llm.completion_stream.remote_gen(
            [{"role": "system", "content": system_prompt}, prompt],
            temp=llm_config["config"]["temp"],
            max_tokens=llm_config["config"]["max_tokens"],
        ):
            response += segment
    else:
        raise Exception(f"Unsupported LLM provider: {state.llm_provider}")

    write_to_debug_log(f"=== LLM RESPONSE ({state.llm_provider}) ===\n")
    write_to_debug_log(response + "\n\n")

    return response


def concat_current_llm_prompt(prompt):
    state = get_current_state()
    if not prompt[-1] == ">":
        state.llm_prompt = state.llm_prompt + "\n"

    state.llm_prompt = state.llm_prompt + prompt
    return
