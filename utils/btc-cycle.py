#!/usr/bin/env python3
"""
=======================================================================
  BTC CYCLE PROJECTION v3
  Pure Python — zero external dependency (stdlib only)
  Compatible: Python 3.6+, Termux armeabi-v7a

  PERUBAHAN dari v2:
  - Pairing siklus berbasis KRONOLOGI, bukan indeks array
    (robust terhadap jumlah tops/bottoms yang tidak simetris)
  - Validasi data: deteksi entri yang tidak membentuk siklus valid
  - Peringatan jika ada entri "orphan" (tidak berpasangan)
  - Default data diperbarui sesuai koreksi pengguna
=======================================================================
  Data disimpan di: btc_data.json (otomatis dibuat jika belum ada)
  Jalankan: python3 btc_cycle_v3.py
=======================================================================
"""

import json
import math
import os
import sys
from datetime import date, datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE  = os.path.join(SCRIPT_DIR, "btc_data.json")

# ──────────────────────────────────────────────────────────────────────
# DATA DEFAULT
# Struktur siklus yang benar (kronologis):
#   Siklus 1: Top Nov2013 → Bottom Jan2015 → Top Des2017
#   Siklus 2: Top Des2017 → Bottom Des2018 → Top Nov2021
#   Siklus 3: Top Nov2021 → Bottom Nov2022 → Top Okt2025
#
# Catatan:
#   - Bottom Okt2011 ($2) disimpan di "pre_bottoms" karena tidak ada
#     Top sebelumnya dalam dataset ini. Ia tidak dipakai untuk
#     kalkulasi siklus, hanya sebagai referensi historis.
#   - $19,666 (Des 2017) adalah harga CLOSE bulanan ATH Des 2017,
#     bukan bottom — jangan masukkan ke array bottoms.
# ──────────────────────────────────────────────────────────────────────
DEFAULT_DATA = {
    "tops": [
        {"date": "2013-11-30", "price": 1163.00,   "note": "Bitstamp"},
        {"date": "2017-12-17", "price": 19798.68,  "note": "Bitstamp (wick high)"},
        {"date": "2021-11-10", "price": 69000.00,  "note": "Binance"},
        {"date": "2025-10-05", "price": 126272.00, "note": "Bitstamp"},
    ],
    "bottoms": [
        {"date": "2015-01-14", "price": 152.00,    "note": "Bitstamp"},
        {"date": "2018-12-15", "price": 3122.00,   "note": "Bitstamp"},
        {"date": "2022-11-21", "price": 15479.00,  "note": "Binance"},
    ],
    "notes": [
        "Bottom pra-siklus: 2011-10-20 $2.00 (Bitstamp) — tidak ada Top sebelumnya, tidak dipakai untuk kalkulasi siklus.",
        "$19,666 (2017-12-17) adalah harga close bulanan ATH Des 2017, bukan Bottom."
    ]
}

# ──────────────────────────────────────────────────────────────────────
# UTIL: WARNA TERMINAL (ANSI)
# ──────────────────────────────────────────────────────────────────────
USE_COLOR = sys.stdout.isatty()

def c(text, code):
    if not USE_COLOR:
        return str(text)
    return f"\033[{code}m{text}\033[0m"

def bold(t):   return c(t, "1")
def yellow(t): return c(t, "33")
def green(t):  return c(t, "32")
def red(t):    return c(t, "31")
def cyan(t):   return c(t, "36")
def gray(t):   return c(t, "90")
def white(t):  return c(t, "97")
def magenta(t):return c(t, "35")

def sep(char="─", n=66):
    print(gray(char * n))

def header(title):
    sep("═")
    print(bold(white(f"  {title}")))
    sep("═")

# ──────────────────────────────────────────────────────────────────────
# UTIL: TANGGAL
# ──────────────────────────────────────────────────────────────────────
def parse_date(s):
    return datetime.strptime(s.strip(), "%Y-%m-%d").date()

def days_between(d1_str, d2_str):
    return (parse_date(d2_str) - parse_date(d1_str)).days

def add_days(d_str, n):
    return (parse_date(d_str) + timedelta(days=int(n))).strftime("%Y-%m-%d")

# ──────────────────────────────────────────────────────────────────────
# UTIL: STATISTIK (pure Python)
# ──────────────────────────────────────────────────────────────────────
def mean(arr):
    return sum(arr) / len(arr)

def weighted_mean(arr, weights=None):
    n = len(arr)
    if weights is None:
        weights = list(range(1, n + 1))
    total_w = sum(weights)
    return sum(a * w for a, w in zip(arr, weights)) / total_w

def linregress(x, y):
    n = len(x)
    if n < 2:
        return 0.0, mean(y), 0.0
    mx, my = mean(x), mean(y)
    ss_xx = sum((xi - mx) ** 2 for xi in x)
    ss_xy = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    ss_yy = sum((yi - my) ** 2 for yi in y)
    if ss_xx == 0:
        return 0.0, my, 0.0
    slope     = ss_xy / ss_xx
    intercept = my - slope * mx
    r_sq      = (ss_xy ** 2) / (ss_xx * ss_yy) if ss_yy != 0 else 0.0
    return slope, intercept, r_sq

def log_regression_predict(x, y, x_pred):
    """Fit ln(y) ~ linear, berguna untuk diminishing returns."""
    log_y = [math.log(max(yi, 1e-9)) for yi in y]
    slope, intercept, r_sq = linregress(x, log_y)
    return math.exp(slope * x_pred + intercept), r_sq

def median(arr):
    s = sorted(arr)
    n = len(s)
    if n == 0:
        return 0.0
    if n % 2 == 1:
        return float(s[n // 2])
    return (s[n // 2 - 1] + s[n // 2]) / 2.0

def ascii_bar(value, max_val, width=22, char="█"):
    if max_val == 0:
        return gray("░" * width)
    filled = min(width, int(round(abs(value) / abs(max_val) * width)))
    return char * filled + gray("░" * (width - filled))

# ──────────────────────────────────────────────────────────────────────
# LOAD / SAVE DATA
# ──────────────────────────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            d = json.load(f)
        # Pastikan key "notes" ada
        if "notes" not in d:
            d["notes"] = []
        return d
    return json.loads(json.dumps(DEFAULT_DATA))

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(green(f"  [✓] Data disimpan ke {DATA_FILE}"))

# ──────────────────────────────────────────────────────────────────────
# INTI: PAIRING BERBASIS KRONOLOGI
# ──────────────────────────────────────────────────────────────────────
def build_cycles(data):
    """
    Untuk setiap pasangan tops[i] → tops[i+1], cari bottom yang
    tanggalnya jatuh DI ANTARA kedua top tersebut.
    Jika tidak ada, pasangan itu tidak membentuk siklus (dilewati).
    Jika lebih dari satu bottom di antara dua top, ambil yang paling
    rendah harganya (true bottom).

    Return:
      cycles      — list dict siklus yang valid
      orphan_tops — tops yang tidak punya siklus lengkap di kedua sisi
      orphan_bots — bottoms yang tidak jatuh di antara pasangan top manapun
    """
    tops    = sorted(data["tops"],    key=lambda x: x["date"])
    bottoms = sorted(data["bottoms"], key=lambda x: x["date"])

    cycles      = []
    used_bottom_dates = set()

    for i in range(len(tops) - 1):
        t1 = tops[i]
        t2 = tops[i + 1]

        # Cari semua bottom di antara t1 dan t2
        candidates = [
            b for b in bottoms
            if t1["date"] < b["date"] < t2["date"]
        ]

        if not candidates:
            continue  # tidak ada bottom → bukan siklus lengkap

        # Ambil yang harganya terendah (true bottom)
        b = min(candidates, key=lambda x: x["price"])
        used_bottom_dates.add(b["date"])

        d_pb  = days_between(t1["date"], b["date"])
        pct_d = (b["price"] - t1["price"]) / t1["price"] * 100
        d_bt  = days_between(b["date"], t2["date"])
        pct_g = (t2["price"] - b["price"]) / b["price"] * 100
        mult  = t2["price"] / b["price"]

        cycles.append({
            "num"     : i + 1,
            "t1"      : t1, "b": b, "t2": t2,
            "d_pb"    : d_pb,
            "pct_d"   : pct_d,
            "d_bt"    : d_bt,
            "pct_g"   : pct_g,
            "mult"    : mult,
        })

    # Orphan bottoms (tidak terpakai)
    orphan_bots = [b for b in bottoms if b["date"] not in used_bottom_dates]

    return cycles, orphan_bots

def validate_and_warn(data):
    """Cetak peringatan jika ada data yang mencurigakan."""
    tops    = sorted(data["tops"],    key=lambda x: x["date"])
    bottoms = sorted(data["bottoms"], key=lambda x: x["date"])

    warnings = []

    # Bottom yang harganya lebih tinggi dari top di sekitarnya
    for b in bottoms:
        nearby_tops = [t for t in tops if abs(days_between(t["date"], b["date"])) < 400]
        for t in nearby_tops:
            if b["price"] > t["price"] and b["date"] > t["date"]:
                warnings.append(
                    f"  ⚠ Bottom {b['date']} (${b['price']:,.0f}) "
                    f"lebih tinggi dari Top {t['date']} (${t['price']:,.0f}). "
                    f"Kemungkinan tipe data salah."
                )

    # Bottom sebelum top pertama
    if tops and bottoms:
        for b in bottoms:
            if b["date"] < tops[0]["date"]:
                warnings.append(
                    f"  ⚠ Bottom {b['date']} (${b['price']:,.0f}) "
                    f"terjadi sebelum Top pertama ({tops[0]['date']}). "
                    f"Tidak dapat membentuk siklus — tidak dipakai untuk kalkulasi."
                )

    return warnings

# ──────────────────────────────────────────────────────────────────────
# MENU: TAMPILKAN DATA
# ──────────────────────────────────────────────────────────────────────
def show_data(data):
    header("DATA HISTORIS BTC")
    tops    = sorted(data["tops"],    key=lambda x: x["date"])
    bottoms = sorted(data["bottoms"], key=lambda x: x["date"])

    # Gabungkan dan urutkan
    events = [(t["date"], "TOP",    t["price"], t.get("note","")) for t in tops]
    events += [(b["date"], "BOTTOM", b["price"], b.get("note","")) for b in bottoms]
    events.sort(key=lambda x: x[0])

    print(f"\n  {'TANGGAL':<14} {'TIPE':<8} {'HARGA (USD)':>16}  SUMBER")
    sep()
    for ev_date, ev_type, ev_price, ev_note in events:
        if ev_type == "TOP":
            tipe_str  = yellow(bold("TOP    "))
            price_str = yellow(f"${ev_price:>14,.2f}")
        else:
            tipe_str  = red("BOTTOM ")
            price_str = red(f"${ev_price:>14,.2f}")
        print(f"  {ev_date:<14} {tipe_str}  {price_str}  {gray(ev_note)}")

    warnings = validate_and_warn(data)
    if warnings:
        print()
        for w in warnings:
            print(red(w))

    # Tampilkan catatan
    notes = data.get("notes", [])
    if notes:
        print(f"\n  {gray('Catatan:')}")
        for n in notes:
            print(f"  {gray('• ' + n)}")
    print()

# ──────────────────────────────────────────────────────────────────────
# MENU: TAMPILKAN SIKLUS
# ──────────────────────────────────────────────────────────────────────
def show_cycles(data):
    cycles, orphan_bots = build_cycles(data)
    if not cycles:
        print(red("  ✗ Belum ada siklus lengkap yang valid."))
        return

    header(f"DETAIL SIKLUS HISTORIS  ({len(cycles)} siklus valid)")
    max_pb = max(c["d_pb"] for c in cycles)
    max_bt = max(c["d_bt"] for c in cycles)

    for cy in cycles:
        pct_d_str = red(f"{cy['pct_d']:.1f}%")
        pct_g_str = green(f"+{cy['pct_g']:.0f}%")
        pb_bar    = ascii_bar(cy["d_pb"], max_pb, 22)
        bt_bar    = ascii_bar(cy["d_bt"], max_bt, 22)
        siklus_label = bold("Siklus " + str(cy["num"]))
        span = cy["t1"]["date"] + " → " + cy["b"]["date"] + " → " + cy["t2"]["date"]
        print(f"\n  {siklus_label}  ({span})")
        print(f"    ATH Awal  : ${cy['t1']['price']:>12,.2f}  [{cy['t1'].get('note','')}]")
        print(f"    Bottom    : ${cy['b']['price']:>12,.2f}  "
              f"({pct_d_str} dalam {cy['d_pb']} hari)")
        print(f"    ATH Baru  : ${cy['t2']['price']:>12,.2f}  "
              f"({pct_g_str} / {cy['mult']:.1f}x dalam {cy['d_bt']} hari)")
        print(f"    Peak→Bot  : {red(pb_bar)} {cy['d_pb']} hr")
        print(f"    Bot→Top   : {green(bt_bar)} {cy['d_bt']} hr")

    if orphan_bots:
        print(f"\n  {yellow('Bottom tidak terpakai (orphan):')}")
        for b in orphan_bots:
            print(f"    • {b['date']}  ${b['price']:>10,.2f}  {gray(b.get('note',''))}")
    print()

# ──────────────────────────────────────────────────────────────────────
# PROYEKSI
# ──────────────────────────────────────────────────────────────────────
def run_projection(data):
    warnings = validate_and_warn(data)
    if warnings:
        print()
        for w in warnings:
            print(red(w))
        print()

    cycles, orphan_bots = build_cycles(data)

    if not cycles:
        print(red("  ✗ Tidak ada siklus valid. Periksa data Anda."))
        return

    if len(cycles) < 2:
        print(yellow(f"  ⚠ Hanya {len(cycles)} siklus valid — proyeksi kurang akurat."))

    # Pisahkan orphan yang benar-benar tidak terpakai vs
    # "pending bottom" (jatuh setelah top terakhir → akan dipakai sebagai confirmed bottom)
    tops_sorted_warn = sorted(data["tops"], key=lambda x: x["date"])
    last_top_date    = tops_sorted_warn[-1]["date"]
    true_orphans     = [b for b in orphan_bots if b["date"] < last_top_date]
    pending_bottoms  = [b for b in orphan_bots if b["date"] >= last_top_date]

    if pending_bottoms:
        for pb in pending_bottoms:
            print(green(f"  [✓] Bottom terkonfirmasi ditemukan: {pb['date']}  "
                        f"${pb['price']:,.2f} — akan digunakan sebagai bottom siklus ini."))
        print()
    if true_orphans:
        print(yellow(f"  ⚠ {len(true_orphans)} bottom tidak terpasangkan dengan siklus manapun: "
                     + ", ".join(b["date"] for b in true_orphans)))
        print()

    # Arrays metrik
    cyc_nums  = [float(cy["num"]) for cy in cycles]
    d_pb_arr  = [cy["d_pb"]  for cy in cycles]
    pct_d_arr = [cy["pct_d"] for cy in cycles]
    d_bt_arr  = [cy["d_bt"]  for cy in cycles]
    pct_g_arr = [cy["pct_g"] for cy in cycles]

    next_cycle = float(cycles[-1]["num"] + 1)

    # ── Hitung semua metode ──

    # Peak→Bottom: durasi
    pb_simple   = mean(d_pb_arr)
    pb_weighted = weighted_mean(d_pb_arr)
    sl, ic, pb_r2 = linregress(cyc_nums, d_pb_arr)
    pb_linreg   = max(150.0, sl * next_cycle + ic)

    # Peak→Bottom: % decline
    dec_simple   = mean(pct_d_arr)
    dec_weighted = weighted_mean(pct_d_arr)
    sl2, ic2, dec_r2 = linregress(cyc_nums, pct_d_arr)
    dec_linreg   = sl2 * next_cycle + ic2

    # Bottom→Top: durasi
    bt_simple   = mean(d_bt_arr)
    bt_weighted = weighted_mean(d_bt_arr)
    sl3, ic3, bt_r2 = linregress(cyc_nums, d_bt_arr)
    bt_linreg   = max(300.0, sl3 * next_cycle + ic3)

    # Bottom→Top: % gain — diminishing returns → log regression dominan
    gain_simple   = mean(pct_g_arr)
    gain_weighted = weighted_mean(pct_g_arr)
    gain_logreg, gain_lr2 = log_regression_predict(cyc_nums, pct_g_arr, next_cycle)

    # ──────────────────────────────────────────────────────────────────
    # KONSENSUS BERBOBOT R²
    # Logika: metode yang lebih akurat menangkap tren mendapat bobot
    # lebih besar. Rata-rata sederhana/tertimbang tidak memodelkan tren,
    # sehingga mendapat bobot kecil (0.05–0.10) sebagai referensi saja.
    # Regresi mendapat bobot = nilai R²-nya sendiri.
    #
    # Bobot durasi (pb/bt): linreg dengan R² aktual
    # Bobot decline%: linreg dengan R² aktual (menangkap tren drawdown
    #                 yang semakin mengecil tiap siklus)
    # Bobot gain%: log regression dengan R² aktual (menangkap
    #              diminishing returns secara eksponensial)
    # ──────────────────────────────────────────────────────────────────
    W_SIMPLE   = 0.05   # referensi historis, tidak menangkap tren
    W_WEIGHTED = 0.10   # sedikit lebih baik dari simple, tapi bukan regresi

    def r2_weighted_avg(values_and_r2):
        """values_and_r2: list of (value, weight)"""
        total_w = sum(w for _, w in values_and_r2)
        if total_w == 0:
            return mean([v for v, _ in values_and_r2])
        return sum(v * w for v, w in values_and_r2) / total_w

    # Durasi Peak→Bottom
    c_days_pb = r2_weighted_avg([
        (pb_simple,   W_SIMPLE),
        (pb_weighted, W_WEIGHTED),
        (pb_linreg,   max(0.01, pb_r2)),
    ])
    c_days_pb = max(150.0, c_days_pb)

    # % Decline (nilai negatif, linreg menangkap tren melandai)
    c_pct_dec = r2_weighted_avg([
        (dec_simple,   W_SIMPLE),
        (dec_weighted, W_WEIGHTED),
        (dec_linreg,   max(0.01, dec_r2)),
    ])

    # Durasi Bottom→Top
    c_days_bt = r2_weighted_avg([
        (bt_simple,   W_SIMPLE),
        (bt_weighted, W_WEIGHTED),
        (bt_linreg,   max(0.01, bt_r2)),
    ])
    c_days_bt = max(300.0, c_days_bt)

    # % Gain (log regression mendominasi jika R² tinggi)
    c_pct_gain = r2_weighted_avg([
        (gain_simple,   W_SIMPLE),
        (gain_weighted, W_WEIGHTED),
        (gain_logreg,   max(0.01, gain_lr2)),
    ])

    # ── Tampilkan Tren Historis ──
    header(f"METRIK & TREN SIKLUS HISTORIS  ({len(cycles)} siklus valid)")
    print(f"\n  {'Siklus':<10} {'Peak→Bot':>10} {'Decline%':>10} "
          f"{'Bot→Top':>10} {'Gain%':>12} {'Mult':>8}")
    sep()
    max_pb_v = max(d_pb_arr); max_bt_v = max(d_bt_arr)
    for cy in cycles:
        print(f"  Siklus {cy['num']:<3} "
              f"{cy['d_pb']:>7} hr  "
              f"{cy['pct_d']:>8.1f}%  "
              f"{cy['d_bt']:>7} hr  "
              f"{cy['pct_g']:>10.0f}%  "
              f"{cy['mult']:>6.1f}x")
        print(f"  {'':10} {gray(ascii_bar(cy['d_pb'], max_pb_v, 18))} "
              f"{gray(ascii_bar(cy['d_bt'], max_bt_v, 18))}")

    # Tampilkan arah tren
    if len(cycles) >= 2:
        print()
        def trend_arrow(arr):
            # Regresi sederhana: slope naik atau turun?
            x = list(range(len(arr)))
            sl_t, _, _ = linregress(x, arr)
            if abs(sl_t) < 1e-6:
                return gray("→ stabil")
            return green("↑ naik") if sl_t > 0 else red("↓ turun")

        dec_abs = [abs(v) for v in pct_d_arr]
        print(f"  Tren drawdown     : {trend_arrow(dec_abs)}  "
              f"{gray('(semakin kecil = bear market lebih ringan)')}")
        print(f"  Tren gain         : {trend_arrow(pct_g_arr)}  "
              f"{gray('(diminishing returns tiap siklus)')}")
        print(f"  Tren durasi bot   : {trend_arrow(d_bt_arr)}  "
              f"{gray('(durasi bull run)')}")

    # ── ATH Terakhir ──
    tops_sorted  = sorted(data["tops"], key=lambda x: x["date"])
    current_top  = tops_sorted[-1]
    ct_date      = current_top["date"]
    ct_price     = current_top["price"]

    # ── Deteksi: apakah sudah ada bottom terkonfirmasi setelah top terakhir? ──
    # Jika ya, gunakan bottom tersebut langsung (skip proyeksi bottom)
    all_bottoms_sorted = sorted(data["bottoms"], key=lambda x: x["date"])
    confirmed_bot = None
    for b in all_bottoms_sorted:
        if b["date"] > ct_date:
            # Bottom setelah top terakhir = bottom siklus ini sudah terkonfirmasi
            if confirmed_bot is None or b["price"] < confirmed_bot["price"]:
                confirmed_bot = b

    bottom_is_confirmed = confirmed_bot is not None

    if bottom_is_confirmed:
        # ── Mode: Bottom Sudah Terkonfirmasi → Langsung Proyeksi ATH ──
        c_bot_date  = confirmed_bot["date"]
        c_bot_price = confirmed_bot["price"]
        actual_d_pb   = days_between(ct_date, c_bot_date)
        actual_pct_d  = (c_bot_price - ct_price) / ct_price * 100

        header(f"BOTTOM SIKLUS {int(next_cycle)} — TERKONFIRMASI")
        print(green(f"\n  [✓] Bottom sudah ada di data — tidak perlu diproyeksikan.\n"))
        print(f"  ATH Referensi : {yellow(ct_date)}  ${yellow(f'{ct_price:,.2f}')}")
        print(f"  Bottom        : {green(c_bot_date)}  ${green(f'{c_bot_price:,.2f}')}")
        print(f"  Durasi        : {actual_d_pb} hari dari ATH")
        print(f"  Penurunan     : {red(f'{actual_pct_d:.1f}%')}")
        bot_range = (c_bot_price, c_bot_price)
        # Tidak ada range — harga sudah pasti
    else:
        # ── Mode: Bottom Belum Ada → Proyeksi Bottom ──
        header(f"PROYEKSI BOTTOM — SIKLUS {int(next_cycle)}")
        print(gray("  Konsensus = rata-rata berbobot R2. Metode R2 tinggi lebih dominan."))
        print(f"\n  ATH Referensi : {yellow(ct_date)}  ${yellow(f'{ct_price:,.2f}')}\n")
        print(f"  {'Metode':<34} {'Bobot':>6}  {'Hari':>5}  {'Decline%':>9}  {'Harga Est.':>14}")
        sep()

        bot_rows = [
            ("Rata-rata Sederhana",               W_SIMPLE,           pb_simple,  dec_simple),
            ("Rata-rata Tertimbang",              W_WEIGHTED,          pb_weighted,dec_weighted),
            (f"Regresi Linear (R2={pb_r2:.2f})",  max(0.01, pb_r2),   pb_linreg,  dec_linreg),
        ]
        bot_estimates = []
        for name, w, est_d, est_pct in bot_rows:
            est_d_int = max(150, int(round(est_d)))
            est_price = max(1.0, ct_price * (1 + est_pct / 100))
            bot_estimates.append((est_d_int, est_pct, est_price))
            marker = bold(yellow(" *")) if w == max(r[1] for r in bot_rows) else "  "
            print(f"  {name:<34} {w:>5.2f}{marker} {est_d_int:>5}  "
                  f"{est_pct:>8.1f}%  ${est_price:>13,.0f}")

        c_bot_date  = add_days(ct_date, int(round(c_days_pb)))
        c_bot_price = max(1.0, ct_price * (1 + c_pct_dec / 100))
        sep()
        print(f"  {bold(yellow('* KONSENSUS (bobot R2)')):<44} "
              f"{int(round(c_days_pb)):>5}  "
              f"{c_pct_dec:>8.1f}%  {green('$'+f'{c_bot_price:,.0f}')}")
        print(f"  {gray('  Tanggal estimasi: '+c_bot_date)}")
        bot_range = (min(e[2] for e in bot_estimates), max(e[2] for e in bot_estimates))

    # ── Output: Proyeksi ATH ──
    ath_cycle_num = int(next_cycle + 1) if not bottom_is_confirmed else int(next_cycle + 1)
    bot_label = "Terkonfirmasi" if bottom_is_confirmed else "Estimasi"
    header(f"PROYEKSI ATH — SIKLUS {ath_cycle_num}")
    print(f"\n  Bottom ({bot_label}) : {green(c_bot_date)}  ~${green(f'{c_bot_price:,.0f}')}\n")
    print(f"  {'Metode':<34} {'Bobot':>6}  {'Hari':>5}  {'Gain%':>9}  {'Harga Est.':>14}")
    sep()

    top_rows = [
        ("Rata-rata Sederhana",                   W_SIMPLE,             bt_simple,   gain_simple),
        ("Rata-rata Tertimbang",                  W_WEIGHTED,           bt_weighted, gain_weighted),
        (f"Log Regresi gain (R2={gain_lr2:.2f})", max(0.01, gain_lr2),  bt_weighted, gain_logreg),
        (f"Lin Reg durasi   (R2={bt_r2:.2f})",    max(0.01, bt_r2),     bt_linreg,   gain_logreg),
    ]
    top_estimates = []
    for name, w, est_d, est_pct in top_rows:
        est_d_int = max(300, int(round(est_d)))
        est_price = c_bot_price * (1 + est_pct / 100)
        top_estimates.append((est_d_int, est_pct, est_price))
        marker = bold(yellow(" *")) if w == max(r[1] for r in top_rows) else "  "
        print(f"  {name:<34} {w:>5.2f}{marker} {est_d_int:>5}  "
              f"{est_pct:>8.0f}%  ${est_price:>13,.0f}")

    c_top_date  = add_days(c_bot_date, int(round(c_days_bt)))
    c_top_price = c_bot_price * (1 + c_pct_gain / 100)
    sep()
    print(f"  {bold(yellow('* KONSENSUS (bobot R2)')):<44} "
          f"{int(round(c_days_bt)):>5}  "
          f"{c_pct_gain:>8.0f}%  {green('$'+f'{c_top_price:,.0f}')}")
    print(f"  {gray('  Tanggal estimasi: '+c_top_date)}")
    top_range = (min(e[2] for e in top_estimates), max(e[2] for e in top_estimates))

    # ── Ringkasan ──
    header("RINGKASAN PROYEKSI")
    bot_status = green("TERKONFIRMASI") if bottom_is_confirmed else yellow("ESTIMASI")
    if bottom_is_confirmed:
        actual_d_pb  = days_between(ct_date, c_bot_date)
        actual_pct_d = (c_bot_price - ct_price) / ct_price * 100
        bot_detail = (
            f"    Jarak ATH: {actual_d_pb} hari (aktual)\n"
            f"    Turun    : {red(f'{actual_pct_d:.1f}%')} (aktual)"
        )
    else:
        bot_detail = (
            f"    Jarak ATH: ~{int(round(c_days_pb))} hari (proyeksi)\n"
            f"    Turun    : {red(f'{c_pct_dec:.1f}%')} (proyeksi)\n"
            f"    Range    : ${bot_range[0]:,.0f}  -  ${bot_range[1]:,.0f}"
        )

    siklus_ath_prev  = str(int(next_cycle) - 1)
    siklus_bot_curr  = str(int(next_cycle))
    siklus_ath_next  = str(int(next_cycle) + 1)

    print(f"""
  {bold('ATH Siklus ' + siklus_ath_prev + ' (Terkonfirmasi)')}
    Tanggal  : {yellow(ct_date)}
    Harga    : {yellow('$'+f'{ct_price:,.2f}')}

  {bold('Bottom Siklus ' + siklus_bot_curr)}  [{bot_status}]
    Tanggal  : {green(c_bot_date)}
    Harga    : {green('$'+f'{c_bot_price:,.2f}')}
{bot_detail}

  {bold('Estimasi ATH Siklus ' + siklus_ath_next)}
    Tanggal  : {green(c_top_date)}
    Harga    : {green('~$'+f'{c_top_price:,.0f}')}
    Jarak Bot: ~{int(round(c_days_bt))} hari
    Naik     : {yellow('+'+f'{c_pct_gain:.0f}%')}
    Range    : ${top_range[0]:,.0f}  -  ${top_range[1]:,.0f}
""")
    print(red("""  ⚠  DISCLAIMER:
  Proyeksi ini hanya referensi statistik berbasis pola historis.
  Bukan prediksi, bukan saran investasi.
  N siklus sangat kecil → interval ketidakpastian sangat lebar.
"""))

# ──────────────────────────────────────────────────────────────────────
# INPUT HELPERS
# ──────────────────────────────────────────────────────────────────────
def input_date(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            d = parse_date(raw)
            return str(d)
        except ValueError:
            print(red("  ✗ Format salah. Gunakan YYYY-MM-DD (contoh: 2026-11-15)"))

def input_price(prompt):
    while True:
        raw = input(prompt).strip().replace(",", "")
        try:
            p = float(raw)
            if p <= 0:
                raise ValueError
            return p
        except ValueError:
            print(red("  ✗ Masukkan angka positif (contoh: 23500 atau 23500.50)"))

def add_top(data):
    header("TAMBAH DATA TOP (ATH)")
    d = input_date("  Tanggal (YYYY-MM-DD) : ")
    p = input_price("  Harga (USD)          : ")
    n = input("  Sumber/catatan       : ").strip() or "manual"
    data["tops"].append({"date": d, "price": p, "note": n})
    data["tops"].sort(key=lambda x: x["date"])
    save_data(data)
    print(green(f"  [✓] Top {d} @ ${p:,.2f} ditambahkan."))

def add_bottom(data):
    header("TAMBAH DATA BOTTOM")
    # Peringatan sebelum input
    print(cyan("  Pastikan entri yang dimasukkan benar-benar Bottom"))
    print(cyan("  (harga terendah setelah ATH, bukan harga close ATH).\n"))
    d = input_date("  Tanggal (YYYY-MM-DD) : ")
    p = input_price("  Harga (USD)          : ")
    n = input("  Sumber/catatan       : ").strip() or "manual"
    # Validasi cepat
    tops_sorted = sorted(data["tops"], key=lambda x: x["date"])
    nearest_tops = [t for t in tops_sorted if abs(days_between(t["date"], d)) < 500]
    for t in nearest_tops:
        if p > t["price"] and d > t["date"]:
            print(yellow(f"\n  ⚠ Harga ${p:,.0f} lebih tinggi dari Top {t['date']} "
                         f"(${t['price']:,.0f}).\n     Apakah ini memang Bottom yang benar?"))
            confirm = input("  Lanjutkan? [y/N]: ").strip().lower()
            if confirm != "y":
                print(gray("  Dibatalkan.")); return
            break
    data["bottoms"].append({"date": d, "price": p, "note": n})
    data["bottoms"].sort(key=lambda x: x["date"])
    save_data(data)
    print(green(f"  [✓] Bottom {d} @ ${p:,.2f} ditambahkan."))

def delete_entry(data):
    header("HAPUS DATA")
    t_choice = input("  Hapus (T)op atau (B)ottom? [T/B]: ").strip().upper()
    if t_choice == "T":
        arr, label = data["tops"], "Top"
    elif t_choice == "B":
        arr, label = data["bottoms"], "Bottom"
    else:
        print(red("  ✗ Pilihan tidak valid.")); return
    arr_sorted = sorted(arr, key=lambda x: x["date"])
    for i, e in enumerate(arr_sorted):
        print(f"  {i+1}. {e['date']}  ${e['price']:>12,.2f}  {gray(e.get('note',''))}")
    idx_str = input(f"  Nomor {label} yang dihapus (0=batal): ").strip()
    try:
        idx = int(idx_str)
        if idx == 0: return
        target = arr_sorted[idx - 1]
        arr.remove(target)
        save_data(data)
        print(green(f"  [✓] Dihapus: {target['date']} @ ${target['price']:,.2f}"))
    except (ValueError, IndexError):
        print(red("  ✗ Nomor tidak valid."))

def reset_to_default(data):
    confirm = input(red("  Yakin reset ke data default? [y/N]: ")).strip().lower()
    if confirm == "y":
        new_data = json.loads(json.dumps(DEFAULT_DATA))
        data.clear(); data.update(new_data)
        save_data(data)
        print(green("  [✓] Data direset ke default."))
    else:
        print(gray("  Dibatalkan."))

def show_notes(data):
    header("CATATAN DATA")
    notes = data.get("notes", [])
    if not notes:
        print(gray("  (Tidak ada catatan)"))
    else:
        for i, n in enumerate(notes):
            print(f"  {i+1}. {n}")
    print(f"\n  {cyan('a')} Tambah catatan  {cyan('d')} Hapus catatan  {cyan('q')} Kembali")
    choice = input("\n  Pilih: ").strip().lower()
    if choice == "a":
        txt = input("  Catatan baru: ").strip()
        if txt:
            data["notes"].append(txt)
            save_data(data)
    elif choice == "d":
        idx_str = input("  Nomor catatan yang dihapus: ").strip()
        try:
            idx = int(idx_str) - 1
            removed = data["notes"].pop(idx)
            save_data(data)
            print(green(f"  [✓] Dihapus: {removed}"))
        except (ValueError, IndexError):
            print(red("  ✗ Nomor tidak valid."))

# ──────────────────────────────────────────────────────────────────────
# MAIN MENU
# ──────────────────────────────────────────────────────────────────────
def print_menu(data):
    tops    = data["tops"]
    bottoms = data["bottoms"]
    cycles, orphans = build_cycles(data)
    warn_str = red(f" ⚠ {len(validate_and_warn(data))} peringatan") \
               if validate_and_warn(data) else green(" ✓ OK")
    print(f"""
  {bold('MENU UTAMA')}  {gray(f'Tops:{len(tops)}  Bottoms:{len(bottoms)}  Siklus valid:{len(cycles)}')} {warn_str}
  {cyan('1')}  Jalankan Proyeksi
  {cyan('2')}  Lihat Data Historis
  {cyan('3')}  Lihat Detail Siklus
  {cyan('4')}  Tambah Top (ATH) Baru
  {cyan('5')}  Tambah Bottom Baru
  {cyan('6')}  Hapus Data
  {cyan('7')}  Catatan
  {cyan('8')}  Reset ke Data Default
  {cyan('0')}  Keluar
""")

def main():
    data = load_data()
    header("BTC CYCLE PROJECTION v3  |  Pure Python  |  stdlib only")
    print(gray(f"  Data file: {DATA_FILE}\n"))

    while True:
        print_menu(data)
        choice = input("  Pilih [0-8]: ").strip()
        print()
        if   choice == "1": run_projection(data)
        elif choice == "2": show_data(data)
        elif choice == "3": show_cycles(data)
        elif choice == "4": add_top(data)
        elif choice == "5": add_bottom(data)
        elif choice == "6": delete_entry(data)
        elif choice == "7": show_notes(data)
        elif choice == "8": reset_to_default(data)
        elif choice == "0":
            print(gray("  Sampai jumpa.\n")); break
        else:
            print(red("  ✗ Pilihan tidak valid.\n"))

if __name__ == "__main__":
    main()
