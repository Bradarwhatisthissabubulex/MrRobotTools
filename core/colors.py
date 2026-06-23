"""Colors and prompt helpers for the green Kali-style UI."""

# ANSI escape helpers
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
UNDERLINE = "\033[4m"

# Green shades (dark -> light) used for the ASCII banner gradient
GREEN_SHADES = [
    "\033[38;5;22m",
    "\033[38;5;28m",
    "\033[38;5;34m",
    "\033[38;5;40m",
    "\033[38;5;46m",
    "\033[38;5;83m",
    "\033[38;5;119m",
    "\033[38;5;155m",
    "\033[38;5;191m",
    "\033[38;5;227m",
]

# Semantic colors
GREEN = "\033[38;5;46m"
BRIGHT_GREEN = "\033[92m"
DARK_GREEN = "\033[38;5;28m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
GREY = "\033[90m"
WHITE = "\033[97m"


def gradient(text_lines):
    """Apply a green gradient across ASCII-art lines (one shade per line)."""
    out = []
    n = len(GREEN_SHADES)
    for i, line in enumerate(text_lines):
        color = GREEN_SHADES[i % n]
        out.append(f"{color}{line}{RESET}")
    return "\n".join(out)


def color(text, c):
    """Wrap text in a color code."""
    return f"{c}{text}{RESET}"


def prompt(path="~/mrrobot"):
    """One-line prompt: (admin@mrrobot)-[path]$"""
    return f"{GREEN}(admin@mrrobot)-[{path}]{GREY}${RESET} "


def print_section(title, count=None):
    """Print a section header like [Pentesting] (6 tools)."""
    if count is not None:
        print(f"\n{BOLD}{DARK_GREEN}[{title}]{RESET} {GREY}({count} tools){RESET}")
    else:
        print(f"\n{BOLD}{DARK_GREEN}[{title}]{RESET}")


def print_tool(num, name, desc=""):
    """Print a numbered tool entry."""
    num_str = f"{num:02d}"
    print(f"  {DARK_GREEN}[{num_str}]{RESET} {GREEN}{name:<28}{RESET} {GREY}{desc}{RESET}")


def print_info(msg):
    print(f"{CYAN}[i]{RESET} {msg}")


def print_ok(msg):
    print(f"{GREEN}[+]{RESET} {msg}")


def print_warn(msg):
    print(f"{YELLOW}[!]{RESET} {msg}")


def print_err(msg):
    print(f"{RED}[-]{RESET} {msg}")


def hr(width=80):
    """Horizontal rule in dark green."""
    print(f"{DARK_GREEN}{'-' * width}{RESET}")


def clear_screen():
    """Clear the terminal screen (cross-platform)."""
    import os as _os
    _os.system("cls" if _os.name == "nt" else "clear")
