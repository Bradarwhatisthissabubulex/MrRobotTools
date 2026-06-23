"""[08] Wallet Tracker - crypto wallet info via the free Blockchair API."""

from core import http as requests

from core.colors import GREEN, DARK_GREEN, GREY, RED, YELLOW, CYAN, BOLD, RESET, hr


SUPPORTED = {"bitcoin", "ethereum", "litecoin", "bitcoin-cash", "dogecoin"}
SYMBOLS = {
    "bitcoin": "BTC", "ethereum": "ETH", "litecoin": "LTC",
    "bitcoin-cash": "BCH", "dogecoin": "DOGE",
}


def _detect_chain(addr):
    """Guess the chain from the address format."""
    if addr.startswith(("0x", "0X")) and len(addr) == 42:
        return "ethereum"
    if addr.startswith(("D", "bc1")) or (len(addr) in (34, 42) and addr[0] in "13bc"):
        return "bitcoin"
    if addr.startswith("L") or addr.startswith("M") or addr.startswith("ltc1"):
        return "litecoin"
    if addr.startswith("q") or addr.startswith("bitcoincash:"):
        return "bitcoin-cash"
    if addr.startswith("D") and len(addr) == 34:
        return "dogecoin"
    return "bitcoin"


def run():
    print(f"\n{BOLD}{DARK_GREEN}[08] WALLET TRACKER{RESET}")
    hr()
    print(f"{CYAN}[i]{RESET} Supports: {', '.join(SUPPORTED)}")
    print(f"{CYAN}[i]{RESET} Data source: Blockchair public API (read-only, no key needed).\n")
    addr = input(f"{GREEN}Wallet address: {RESET}").strip()
    if not addr:
        print(f"{RED}[-]{RESET} No address provided.")
        return

    chain = input(
        f"{GREEN}Chain  [auto] or specify ({'/'.join(SUPPORTED)}): {RESET}"
    ).strip().lower() or _detect_chain(addr)
    if chain not in SUPPORTED:
        print(f"{RED}[-]{RESET} Unsupported chain.")
        return

    print(f"\n{CYAN}[i]{RESET} Querying Blockchair for {SYMBOLS[chain]} address {BOLD}{addr}{RESET} ...\n")
    try:
        r = requests.get(
            f"https://api.blockchair.com/{chain}/dashboards/address/{addr}",
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        print(f"{RED}[-]{RESET} API request failed: {e}")
        return

    addr_data = data.get("data", {}).get(addr, {})
    if not addr_data:
        print(f"{RED}[-]{RESET} Address not found / no data returned.")
        return

    a = addr_data.get("address", {})
    print(f"{DARK_GREEN}== Address Overview =={RESET}")
    print(f"  {GREEN}Chain:{RESET}            {SYMBOLS.get(chain, chain)} ({chain})")
    print(f"  {GREEN}Balance:{RESET}          {a.get('balance', 'N/A')} satoshis/wei")
    print(f"  {GREEN}Received total:{RESET}   {a.get('received', 'N/A')}")
    print(f"  {GREEN}Spent total:{RESET}      {a.get('spent', 'N/A')}")
    print(f"  {GREEN}TX count:{RESET}         {a.get('transaction_count', 'N/A')}")
    print(f"  {GREEN}First seen:{RESET}       {a.get('first_seen_receiving', 'N/A')}")
    print(f"  {GREEN}Last seen:{RESET}        {a.get('last_seen_receiving', 'N/A')}")
    if a.get("first_seen_spending"):
        print(f"  {GREEN}First spend:{RESET}       {a['first_seen_spending']}")
    if a.get("last_seen_spending"):
        print(f"  {GREEN}Last spend:{RESET}        {a['last_seen_spending']}")

    txs = addr_data.get("transactions", [])[:10]
    if txs:
        print(f"\n{DARK_GREEN}== Recent Transactions (last {len(txs)}) =={RESET}")
        for tx in txs:
            print(f"  {CYAN}{tx}{RESET}")

    print(f"\n{CYAN}[i]{RESET} Full explorer link: {GREY}https://blockchair.com/{chain}/address/{addr}{RESET}")
