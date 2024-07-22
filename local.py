import argparse
import curses
from dotenv import load_dotenv

from state import init_game_state, set_current_state
from splitscreen import SplitScreen
import engine
from utils import format_with_linebreaks

splitscreen = SplitScreen()


def show_output(input_command, game_command, game_response, llm_response):
    """
    For displaying game content to the command line
    """
    columns = splitscreen.col_width
    if input_command:
        input_command = format_with_linebreaks(input_command, columns)
    if game_command:
        game_command = format_with_linebreaks(game_command, columns)
    else:
        game_command = ""
    game_response = format_with_linebreaks(game_response, columns)
    llm_response = format_with_linebreaks(llm_response, columns)

    if game_command:
        splitscreen.output_text("> " + game_command, "> " + input_command)
    splitscreen.output_text(game_response, llm_response)


def game_loop():
    is_game_over = False
    while not is_game_over:
        # Attempt player command
        input_command = splitscreen.get_command()
        input_command, game_command, game_response, llm_response, is_game_over = (
            engine.process_input(input_command)
        )
        show_output(input_command, game_command, game_response, llm_response)


# Entry point
def main(stdscr, game_path, llm="anthropic", tone="pratchett"):
    print(game_path, llm, tone)

    splitscreen.initialize(stdscr)
    new_state = init_game_state(game_path, llm, tone)
    set_current_state(new_state)

    input_command, game_command, game_response, llm_response, is_game_over = (
        engine.start_new_game()
    )
    show_output(input_command, game_command, game_response, llm_response)
    game_loop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("game_path")
    parser.add_argument(
        "-l",
        "--llm",
        help="LLM provider",
        choices=["anthropic", "openai", "hosted"],
        default="anthropic",
    )
    parser.add_argument(
        "-t",
        "--tone",
        help="Tone of rewrite",
        choices=["none", "original", "pratchett", "gumshoe", "legal", "spaceopera"],
        default="none",
    )

    args = parser.parse_args()
    load_dotenv()

    curses.wrapper(main, args.game_path, args.llm, args.tone)
