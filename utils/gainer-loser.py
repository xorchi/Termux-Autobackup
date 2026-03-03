#!/usr/bin/env python3
import sys
import math
import time
from datetime import datetime
import requests

try:
    from colorama import init, Fore, Style
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama", "-q", "--break-system-packages"])
    from colorama import init, Fore, Style

init(autoreset=True)

VS_CURRENCY    = "usd"
PER_PAGE       = 250
MAX_RETRIES    = 5
MIN_MARKET_CAP = 10_000_000
WIDTH          = 44
SEP_HEAVY      = "=" * WIDTH
SEP_LIGHT      = "-" * WIDTH

HEADERS = {
    "User-Agent": "Mozilla/5.0 (XorchiBot/1.0; +https://example.com)"
}

# ─── Helpers ──────────────────────────────────────────────────

def dynamic_price_format(price: float) -> str:
    if price == 0:
        return "0.00"
    elif price >= 1:
        return f"{price:,.2f}"
    else:
        digits = max(2, -int(math.floor(math.log10(abs(price)))) + 2)
        return f"{price:,.{digits}f}"

def fmt_compact(value: float) -> str:
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    return f"${value:,.0f}"

def fmt_change(value) -> str:
    if value is None:
        return "N/A"
    sign = "+" if value >= 0 else ""
    color = Fore.GREEN if value >= 0 else Fore.RED
    return f"{color}{sign}{value:.2f}%{Style.RESET_ALL}"

def print_row(label: str, value: str):
    print(f"  {label:<7}: {value}")

# ─── Fetch ────────────────────────────────────────────────────

def fetch_data() -> list:
    url = (
        f"https://api.coingecko.com/api/v3/coins/markets"
        f"?vs_currency={VS_CURRENCY}&order=market_cap_desc"
        f"&per_page={PER_PAGE}&page=1&sparkline=false&locale=en"
        f"&price_change_percentage=1h,24h,7d,30d"
    )

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 429:
                wait = min(60, 2 ** attempt * 5)
                print(f"{Fore.YELLOW}Rate limited. Waiting {wait}s...{Style.RESET_ALL}")
                time.sleep(wait)
                continue
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            wait = min(60, 2 ** attempt * 5)
            print(f"{Fore.RED}Failed: {e}. Retrying in {wait}s...{Style.RESET_ALL}")
            time.sleep(wait)

    print(f"{Fore.RED}Failed to fetch data after all retries.{Style.RESET_ALL}")
    sys.exit(1)

# ─── Build coin list ──────────────────────────────────────────

def build_coins(raw: list) -> list:
    coins = []
    for c in raw:
        mcap = c.get("market_cap") or 0
        if mcap < MIN_MARKET_CAP:
            continue
        change_30d = c.get("price_change_percentage_30d_in_currency")
        if change_30d is None:
            continue
        coins.append({
            "symbol":     c["symbol"].upper(),
            "price":      c.get("current_price") or 0,
            "mcap":       mcap,
            "volume":     c.get("total_volume") or 0,
            "change_1h":  c.get("price_change_percentage_1h_in_currency"),
            "change_24h": c.get("price_change_percentage_24h_in_currency"),
            "change_7d":  c.get("price_change_percentage_7d_in_currency"),
            "change_30d": change_30d,
        })
    return coins

# ─── Display ──────────────────────────────────────────────────

def print_section(title: str, coins: list):
    print(f"\n{Style.BRIGHT}{title}{Style.RESET_ALL}")
    print(SEP_HEAVY)

    for i, coin in enumerate(coins, 1):
        print(f"{Style.BRIGHT}#{i}  {coin['symbol']}{Style.RESET_ALL}")
        print_row("Price",  f"${dynamic_price_format(coin['price'])}")
        print_row("MCap",   fmt_compact(coin["mcap"]))
        print_row("Vol",    fmt_compact(coin["volume"]))
        print_row("1h",     fmt_change(coin["change_1h"]))
        print_row("24h",    fmt_change(coin["change_24h"]))
        print_row("7d",     fmt_change(coin["change_7d"]))
        print_row("30d",    fmt_change(coin["change_30d"]))
        print(SEP_LIGHT)

# ─── Main ─────────────────────────────────────────────────────

raw   = fetch_data()
coins = build_coins(raw)

if not coins:
    print(f"{Fore.RED}No valid data available. Try again later.{Style.RESET_ALL}")
    sys.exit(1)

top_gainers = sorted(coins, key=lambda x: x["change_30d"], reverse=True)[:10]
top_losers  = sorted(coins, key=lambda x: x["change_30d"])[:10]

print_section("▲ TOP 10 GAINER — 30d  (Top 250 · MCap ≥ $10M)", top_gainers)
print_section("▼ TOP 10 LOSER  — 30d  (Top 250 · MCap ≥ $10M)", top_losers)

ts = datetime.now().strftime("%d %b %Y  %H:%M")
print(f"\n{Style.DIM}Data: CoinGecko  ·  {ts}{Style.RESET_ALL}\n")

