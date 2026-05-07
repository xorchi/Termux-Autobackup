#!/usr/bin/env python3
"""
XMR Supply Calculator
=====================
Deterministically calculates the total amount of XMR mined
up to the current block height, using Monero's official emission formula.

Approach:
- Block height is fetched from a public API (no token required)
- All supply calculations are performed locally (pure mathematics)
- No trust in third parties for the supply figure

Monero Emission Formula:
  Block Reward = floor((M - A) >> 20) in piconero
  where:
    M = 2^64 - 1  (theoretical maximum supply in piconero)
    A = current circulating supply in piconero

Tail Emission (after main emission ends):
  Minimum reward = 0.6 XMR per block (600,000,000,000 piconero)

Usage:
  python3 xmr_supply_calculator.py             # standard output
  python3 xmr_supply_calculator.py --verbose   # include extra stats
  python3 xmr_supply_calculator.py --no-color  # disable ANSI colors
"""

import urllib.request
import json
import sys

# ─────────────────────────────────────────────
# CLI FLAGS
# ─────────────────────────────────────────────

USE_COLOR = "--no-color" not in sys.argv
VERBOSE   = "--verbose"  in sys.argv

# ─────────────────────────────────────────────
# ANSI COLOR HELPERS
# ─────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
ORANGE = "\033[38;5;208m"   # Monero brand color
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"

def c(text: str, *codes: str) -> str:
    """Apply ANSI color codes if color mode is enabled."""
    if not USE_COLOR:
        return text
    return "".join(codes) + text + RESET

# ─────────────────────────────────────────────
# MONERO CONSTANTS
# ─────────────────────────────────────────────

PICONERO       = 1_000_000_000_000      # 1 XMR = 10^12 piconero
M              = 2**64 - 1              # Theoretical max supply (piconero)
TAIL_EMISSION  = 600_000_000_000        # 0.6 XMR in piconero
GENESIS_REWARD = 17_592_186_044_415     # Genesis block reward (piconero)

# Public API endpoints — no token required, tried in order
API_ENDPOINTS = [
    {
        "name"   : "blockchair.com",
        "url"    : "https://api.blockchair.com/monero/stats",
        "parser" : lambda d: int(d["data"]["blocks"]),
    },
    {
        "name"   : "localmonero.co",
        "url"    : "https://localmonero.co/blocks/api/get_stats",
        "parser" : lambda d: int(d["height"]),
    },
    {
        "name"   : "monerohash.com",
        "url"    : "https://monerohash.com/explorer/api/networkinfo",
        "parser" : lambda d: int(d["data"]["height"]),
    },
]

# ─────────────────────────────────────────────
# FETCH BLOCK HEIGHT
# ─────────────────────────────────────────────

def fetch_block_height() -> int:
    """
    Tries each API endpoint in order.
    Returns the current block height.
    Falls back to manual input if all endpoints fail.
    """
    headers = {"User-Agent": "XMR-Supply-Calculator/1.0"}

    for endpoint in API_ENDPOINTS:
        try:
            req = urllib.request.Request(endpoint["url"], headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data   = json.loads(resp.read().decode())
                height = endpoint["parser"](data)
                print(c(f"  [OK]  {endpoint['name']} → block height: {height:,}", DIM))
                return height
        except Exception as e:
            print(c(f"  [--]  {endpoint['name']} failed: {e}", DIM))

    # All endpoints failed — manual fallback
    print()
    print(c("  All API endpoints unreachable.", YELLOW))
    print(c("  You can find the current block height at: https://xmrchain.net", YELLOW))
    print()
    try:
        raw    = input("  Enter block height manually: ").strip()
        height = int(raw)
        return height
    except ValueError:
        print(c("  Invalid input. Exiting.", YELLOW))
        sys.exit(1)

# ─────────────────────────────────────────────
# EMISSION FORMULA
# ─────────────────────────────────────────────

def block_reward(supply_piconero: int) -> int:
    """
    Returns the block reward in piconero for a given supply level.
    Formula: max(floor((M - A) >> 20), TAIL_EMISSION)
    """
    return max((M - supply_piconero) >> 20, TAIL_EMISSION)

# ─────────────────────────────────────────────
# SUPPLY SIMULATION
# ─────────────────────────────────────────────

def calculate_supply(target_height: int) -> dict:
    """
    Simulates every block from 0 to target_height,
    accumulating supply using the deterministic emission formula.
    """
    print()
    print(c(f"  Simulating {target_height:,} blocks — please wait...", DIM))
    print()

    supply            = 0
    tail_started      = False
    tail_start_height = None
    blocks_in_tail    = 0
    last_reward       = 0

    for height in range(target_height):
        reward = GENESIS_REWARD if height == 0 else block_reward(supply)

        if reward == TAIL_EMISSION and not tail_started:
            tail_started      = True
            tail_start_height = height
            print(c(f"  Tail emission activated at block {height:,}", DIM))

        if tail_started:
            blocks_in_tail += 1

        supply      += reward
        last_reward  = reward

        if height % 500_000 == 0 and height > 0:
            print(c(f"  ... block {height:,}  |  {supply / PICONERO:,.2f} XMR", DIM))

    return {
        "supply_xmr"        : supply / PICONERO,
        "last_reward_xmr"   : last_reward / PICONERO,
        "tail_started"      : tail_started,
        "tail_start_height" : tail_start_height,
        "blocks_in_tail"    : blocks_in_tail,
        # verbose only
        "supply_piconero"   : supply,
        "tail_xmr"          : blocks_in_tail * 0.6,
    }

# ─────────────────────────────────────────────
# OUTPUT
# ─────────────────────────────────────────────

def print_results(height: int, r: dict) -> None:
    W = 54
    sep      = c("=" * W, ORANGE)
    sep_thin = c("-" * W, DIM)

    print()
    print(sep)
    print(c("  MONERO (XMR) SUPPLY VERIFICATION", ORANGE, BOLD))
    print(sep)

    # — Primary results (always shown, highlighted) —
    print()
    print(
        "  " +
        c("Block Height  ", WHITE) +
        c(f"{height:>20,}", CYAN, BOLD)
    )
    print(
        "  " +
        c("Total Supply  ", WHITE) +
        c(f"{r['supply_xmr']:>17,.6f} XMR", GREEN, BOLD)
    )
    print(
        "  " +
        c("Last Reward   ", WHITE) +
        c(f"{r['last_reward_xmr']:>17.6f} XMR", YELLOW)
    )
    print()
    print(sep_thin)

    # — Tail emission status —
    if r["tail_started"]:
        status = c("Active", GREEN, BOLD)
        print(f"  {'Tail Emission':<22}{status}")
        print(c(f"  {'Started at block':<22}{r['tail_start_height']:,}", DIM))
        if VERBOSE:
            print(c(f"  {'Blocks in tail':<22}{r['blocks_in_tail']:,}", DIM))
            print(c(f"  {'XMR from tail':<22}{r['tail_xmr']:,.2f} XMR", DIM))
    else:
        print(f"  {'Tail Emission':<22}" + c("Not yet active", DIM))

    # — Verbose extras —
    if VERBOSE:
        print(sep_thin)
        print(c(f"  Supply (piconero)      {r['supply_piconero']:,}", DIM))

    print()
    print(sep)
    print(c("  METHODOLOGY", WHITE, BOLD))
    print(sep_thin)
    print(c("  * Block height  : fetched from public API (no token)", DIM))
    print(c("  * Supply calc   : local deterministic math only", DIM))
    print(c("  * Formula       : max((2^64-1 - supply) >> 20, 0.6 XMR)", DIM))
    print(c("  * Trust model   : zero trust on supply figures", DIM))
    print(c("  * Reproducible  : same height = same result, always", DIM))
    print(sep)
    print()

# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

def main():
    W = 54
    print()
    print(c("=" * W, ORANGE))
    print(c("  XMR SUPPLY CALCULATOR", ORANGE, BOLD))
    print(c("  Deterministic Verification — Zero Trust", DIM))
    print(c("=" * W, ORANGE))
    print()
    print(c("  Fetching block height...", DIM))
    print()

    height = fetch_block_height()
    result = calculate_supply(height)
    print_results(height, result)

if __name__ == "__main__":
    main()
