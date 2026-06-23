"""Authorization gate. Shown at startup, requires typing 'I agree'."""

import time

from .colors import (
    RED, YELLOW, GREEN, DARK_GREEN, GREY, CYAN, BOLD, RESET, hr
)


AUTH_TEXT = f"""
{RED}{BOLD}==================== ETHICAL USE AUTHORIZATION ===================={RESET}

{YELLOW}MrRobotTools{RESET} is a security & OSINT toolkit intended {BOLD}strictly{RESET} for:

    {GREEN}1.{RESET} Authorized penetration testing on systems YOU OWN or have
       {BOLD}written permission{RESET} to test.
    {GREEN}2.{RESET} Defensive security research, education, and CTF practice.
    {GREEN}3.{RESET} Investigating publicly-available information (OSINT) about
       your own assets, brand, or identity.

{RED}It is ILLEGAL to use these tools against systems you do not own or do
not have explicit written authorization to test.{RESET} Unauthorized scanning,
port probing, credential harvesting, or website cloning may violate
computer-fraud, privacy, and telecommunications laws in most jurisdictions
(e.g. US CFAA, UK Computer Misuse Act, EU GDPR, etc.) and can carry
criminal penalties.

By proceeding you confirm that:
  {GREEN}[a]{RESET} You will only use these tools on systems you own or are
       authorized to test.
  {GREEN}[b]{RESET} You accept full legal responsibility for your actions.
  {GREEN}[c]{RESET} You will not use MrRobotTools to harm, harass, or steal
       from any third party.

{RED}{BOLD}=================================================================={RESET}
"""


def require_authorization():
    """Block until the user types 'I agree'. Returns True if accepted."""
    print(AUTH_TEXT)
    time.sleep(0.3)
    hr()
    attempts = 0
    while True:
        try:
            ans = input(
                f"{GREEN}(admin@mrrobot)-[auth]{GREY}${RESET} "
                f"Type {BOLD}'I agree'{RESET}{GREY} to continue, or 'exit' to quit: {RESET}"
            ).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nAuthorization not given. Exiting.")
            return False

        if ans in ("i agree", "iagree", "agree", "yes", "y"):
            print(f"\n{GREEN}[+]{RESET} Authorization accepted. Welcome, admin.")
            time.sleep(0.5)
            return True
        if ans in ("exit", "quit", "no", "n", ""):
            print(f"\n{RED}[-]{RESET} Authorization declined. Goodbye.")
            return False
        attempts += 1
        print(f"{YELLOW}[!]{RESET} Unrecognized response. Type {BOLD}'I agree'{RESET} or {BOLD}'exit'{RESET}.")
        if attempts >= 3:
            print(f"{RED}[-]{RESET} Too many invalid attempts. Exiting.")
            return False
