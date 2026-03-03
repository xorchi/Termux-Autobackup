import subprocess
import json
import sys

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price?ids=monero&vs_currencies=usd,idr"
EXCHANGE_URL = "https://api.exchangerate.host/latest?base=USD&symbols=IDR"


def curl_get(url):
    try:
        result = subprocess.run(
            ["curl", "-4", "-s", url],
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode != 0:
            return None

        return json.loads(result.stdout)

    except Exception:
        return None


def get_prices():
    data = curl_get(COINGECKO_URL)
    if not data or "monero" not in data:
        return None, None, None

    xmr_usd = data["monero"]["usd"]
    xmr_idr = data["monero"]["idr"]

    # fallback USD → IDR if needed
    if not xmr_idr:
        ex = curl_get(EXCHANGE_URL)
        if ex and "rates" in ex:
            usd_idr = ex["rates"]["IDR"]
            xmr_idr = xmr_usd * usd_idr
        else:
            usd_idr = None
    else:
        usd_idr = xmr_idr / xmr_usd

    return xmr_usd, xmr_idr, usd_idr


def print_prices(xmr_usd, xmr_idr, usd_idr):
    print("╭──────────── 📊 Harga Terkini ────────────╮")
    print(f"│ ɱ → Rp : {xmr_idr:,.0f}" if xmr_idr else "│ ɱ → Rp : N/A")
    print(f"│ ɱ → $  : {xmr_usd:,.2f}" if xmr_usd else "│ ɱ → $  : N/A")
    print(f"│ $  → Rp : {usd_idr:,.0f}" if usd_idr else "│ $  → Rp : N/A")
    print("╰──────────────────────────────────────────╯")


def convert_menu(xmr_usd, xmr_idr, usd_idr):
    while True:
        print("╭─────────── 🔁 Convert ───────────────────╮")
        print("│ 1. ɱ → Rp                                │")
        print("│ 2. Rp → ɱ                                │")
        print("│ 3. ɱ → $                                 │")
        print("│ 4. $  → ɱ                                │")
        print("│ 5. $  → Rp                               │")
        print("│ 6. Rp → $                                │")
        print("│ q. Quit                                  │")
        print("╰──────────────────────────────────────────╯")

        choice = input("Choice: ")

        if choice == "q":
            sys.exit()

        try:
            amount = float(input("Jumlah: "))
        except:
            print("Invalid input\n")
            continue

        if choice == "1" and xmr_idr:
            print(f"Hasil: Rp {amount * xmr_idr:,.0f}\n")

        elif choice == "2" and xmr_idr:
            print(f"Hasil: {amount / xmr_idr:.6f} ɱ\n")

        elif choice == "3" and xmr_usd:
            print(f"Hasil: $ {amount * xmr_usd:,.2f}\n")

        elif choice == "4" and xmr_usd:
            print(f"Hasil: {amount / xmr_usd:.6f} ɱ\n")

        elif choice == "5" and usd_idr:
            print(f"Hasil: Rp {amount * usd_idr:,.0f}\n")

        elif choice == "6" and usd_idr:
            print(f"Hasil: $ {amount / usd_idr:.2f}\n")

        else:
            print("Price data not available\n")


def main():
    xmr_usd, xmr_idr, usd_idr = get_prices()

    if not xmr_usd:
        print("❌ Failed to fetch price from API")
        return

    print_prices(xmr_usd, xmr_idr, usd_idr)
    convert_menu(xmr_usd, xmr_idr, usd_idr)


if __name__ == "__main__":
    main()
