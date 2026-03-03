from pycoingecko import CoinGeckoAPI
import math
from colorama import init, Fore, Style

# Initialize colorama for terminal color support
init()

def dynamic_price_format(price):
    """Format price dynamically with enough significant decimals"""
    if price == 0:
        return "0"
    elif price >= 1:
        return f"{price:,.2f}"
    else:
        digits = max(2, -int(math.floor(math.log10(abs(price)))) + 2)
        return f"{price:,.{digits}f}"

def split_price(price_str):
    """Split integer & decimal for decimal point alignment"""
    if '.' in price_str:
        integer, decimal = price_str.split('.')
        return integer, decimal
    else:
        return price_str, ''

def format_percentage(change):
    """Format 30-day percentage change with color, no decimals"""
    if change is None or change == '':
        return f"{Fore.RED}N/A{Style.RESET_ALL}"
    try:
        change_float = float(change)
        color = Fore.GREEN if change_float > 0 else Fore.RED
        return f"{color}{change_float:+.0f}%{Style.RESET_ALL}"
    except (ValueError, TypeError):
        return f"{Fore.RED}N/A{Style.RESET_ALL}"

if __name__ == "__main__":
    try:
        # Fetch data from API with price_change_percentage parameter
        cg = CoinGeckoAPI()
        coins = cg.get_coins_markets(
            vs_currency='usd',
            order='market_cap_desc',
            per_page=100,
            page=1,
            price_change_percentage='30d'  # Request 30-day price change data
        )

        # Format price, percentage, and split
        price_data = []
        for coin in coins:
            price_str = dynamic_price_format(coin['current_price'])
            integer, decimal = split_price(price_str)
            # Use 30d data, fallback to 24h if unavailable
            change = coin.get('price_change_percentage_30d_in_currency', coin.get('price_change_percentage_24h_in_currency', None))
            price_data.append({
                'rank': coin['market_cap_rank'],
                'ticker': coin['symbol'].upper(),
                'integer': integer,
                'decimal': decimal,
                'change_30d': change
            })

        # Determine column widths for integer, decimal, and percentage
        int_width = max(len(p['integer']) for p in price_data)
        dec_width = max(len(p['decimal']) for p in price_data)
        change_width = max(len(format_percentage(p['change_30d']).replace(Fore.RED, '').replace(Fore.GREEN, '').replace(Style.RESET_ALL, '')) for p in price_data)

        # Print header
        header = f"{'Rank':<5} {'Ticker':<10} {'Price (USD)':>{int_width + 1 + dec_width}} {'% 30D':>{change_width}}"
        print(header)
        print("-" * len(header))

        # Print data
        for p in price_data:
            price_formatted = f"{p['integer'].rjust(int_width)}.{p['decimal'].ljust(dec_width)}"
            change_formatted = format_percentage(p['change_30d']).rjust(change_width + len(Fore.GREEN) + len(Style.RESET_ALL))
            print(f"{p['rank']:<5} {p['ticker']:<10} {price_formatted:>{int_width + 1 + dec_width}} {change_formatted}")

    except Exception as e:
        print(f"Failed to fetch data from API. Check your internet connection or CoinGecko API status: {str(e)}")
