"""MrRobot ASCII banner + screen-render helper.

Every view in the app calls render_screen() so the terminal clears,
the banner reprints at the top, then the view's content draws below.
"""

import shutil

from .colors import (
    gradient, GREEN, DARK_GREEN, GREY, BOLD, RESET, clear_screen,
)

# MrRobot figlet ASCII (5 lines -> clean green gradient)
ROBOT_LINES = [
    "    __  ___     ____        __          __ ",
    "   /  |/  /____/ __ \\____  / /_  ____  / /_",
    "  / /|_/ / ___/ /_/ / __ \\/ __ \\/ __ \\/ __/",
    " / /  / / /  / _, _/ /_/ / /_/ / /_/ / /_  ",
    "/_/  /_/_/  /_/ |_|\\____/_.___/\\____/\\__/  ",
]

SUBTITLE = "M  R  R  O  B  O  T  T  O  O  L  S"
TAGLINE = "Control is an illusion. So is freedom."


def _term_width(default=80):
    """Get terminal width, with a sensible fallback."""
    try:
        return max(shutil.get_terminal_size((default, 24)).columns, 40)
    except Exception:
        return default


def _center_line(text):
    """Center a string (which may contain ANSI codes) in the terminal."""
    import re
    visible = re.sub(r"\033\[[0-9;]*m", "", text)
    width = _term_width()
    pad = max(0, (width - len(visible)) // 2)
    return " " * pad + text


def show_banner():
    """Print the green-gradient MrRobot figlet + subtitle, centered."""
    print()
    colored = gradient(ROBOT_LINES).split("\n")
    for line in colored:
        print(_center_line(line))
    print(_center_line(f"{BOLD}{GREEN}{SUBTITLE}{RESET}"))
    print(_center_line(f"{GREY}{TAGLINE}{RESET}"))
    width = len(SUBTITLE) + 4
    print(_center_line(f"{DARK_GREEN}{'=' * width}{RESET}"))


def render_screen(content=None):
    """Clear screen, show banner, then draw content (callable or string)."""
    clear_screen()
    show_banner()
    if content is None:
        return
    if callable(content):
        content()
    else:
        print(content)
