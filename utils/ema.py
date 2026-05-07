#!/usr/bin/env python3
"""
EMA 200 Screener — Top 100 Coins
Menampilkan koin yang closing candle daily-nya DI ATAS EMA 200.
Binance REST API via urllib — zero dependency, pure Python.
Jalankan: python 100.py
"""

import urllib.request
import json
import time

# --- Konfigurasi ---
TOP_N       = 100
EMA_PERIOD  = 200
TIMEFRAME   = "1d"
QUOTE       = "USDT"
BASE_URL    = "https://api.binance.com"

STABLECOINS = {
    "USDT","USDC","BUSD","DAI","TUSD","USDP","USDD","GUSD",
    "FRAX","LUSD","SUSD","EURS","XAUT","FDUSD","PYUSD",
    "USDE","USDS","USDX","UST","USTC", "USD1", "EUR"
}

# --- Helpers ---
def get(path: str, params: dict = {}) -> any:
    query = "&".join(f"{k}={v}" for k, v in params.items())
    url   = f"{BASE_URL}{path}?{query}" if query else f"{BASE_URL}{path}"
    req   = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def hitung_ema(closes: list, period: int) -> list:
    if len(closes) < period:
        return []
    k   = 2 / (period + 1)
    ema = [sum(closes[:period]) / period]
    for p in closes[period:]:
        ema.append(p * k + ema[-1] * (1 - k))
    return ema

# --- Main ---
def main():
    print("\nMengambil data ticker 24 jam...")
    tickers = get("/api/v3/ticker/24hr")

    # Filter USDT, bukan stablecoin, ASCII only, urutkan by volume
    filtered = []
    for t in tickers:
        sym  = t["symbol"]
        if not sym.endswith(QUOTE):
            continue
        if not sym.isascii():
            continue
        base = sym[:-len(QUOTE)]
        if base in STABLECOINS:
            continue
        vol = float(t.get("quoteVolume") or 0)
        if vol > 0:
            filtered.append((sym, vol))

    filtered.sort(key=lambda x: x[1], reverse=True)
    top = [sym for sym, _ in filtered[:TOP_N]]

    print(f"Memeriksa EMA {EMA_PERIOD} pada {len(top)} koin...\n")

    hasil = []
    gagal = []

    for i, symbol in enumerate(top, 1):
        try:
            klines = get("/api/v3/klines", {
                "symbol":   symbol,
                "interval": TIMEFRAME,
                "limit":    EMA_PERIOD + 10
            })

            if len(klines) < EMA_PERIOD + 2:
                continue

            closes = [float(k[4]) for k in klines]
            ema    = hitung_ema(closes, EMA_PERIOD)

            if len(ema) < 1:
                continue

            c_now = closes[-1]
            e_now = ema[-1]

            # Kondisi: closing candle terbaru di atas EMA 200
            if c_now > e_now:
                jarak = ((c_now - e_now) / e_now) * 100
                hasil.append((symbol, c_now, e_now, jarak))

            if i % 10 == 0:
                print(f"  [{i}/{len(top)}] diproses...")

            time.sleep(0.1)

        except Exception as e:
            gagal.append(symbol)
            continue

    # Urutkan berdasarkan jarak terkecil ke terbesar (paling dekat EMA dulu)
    hasil.sort(key=lambda x: x[3])

    # --- Output ---
    print("\n" + "="*58)
    print(f"   EMA {EMA_PERIOD} DAILY SCREENER — CLOSING DI ATAS EMA")
    print("="*58)

    if not hasil:
        print("  Tidak ada koin yang closing di atas EMA 200.")
    else:
        print(f"  Ditemukan {len(hasil)} koin (diurutkan: jarak terkecil dulu):\n")
        print(f"  {'No':<4} {'Symbol':<14} {'Close':>10} {'EMA200':>10} {'Jarak':>8}")
        print(f"  {'-'*52}")
        for idx, (sym, c, e, j) in enumerate(hasil, 1):
            print(f"  {idx:<4} {sym:<14} {c:>10.4f} {e:>10.4f} {j:>7.2f}%")

    if gagal:
        print(f"\n  Gagal ({len(gagal)}): {', '.join(gagal)}")

    print("="*58)
    print(f"  Diperiksa: {len(top)} koin | Binance REST API")
    print("="*58 + "\n")

if __name__ == "__main__":
    main()
