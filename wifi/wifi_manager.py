#!/usr/bin/env python3
"""
WiFi Credential Manager
Backend: SQLite (dengan migrasi otomatis dari wifi.json jika ada)
"""

import json
import random
import sqlite3
import string
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ── Dependency check & auto-install ──────────────────────────────────────────
def ensure_deps():
    import importlib
    for pkg, mod in [("qrcode", "qrcode"), ("colorama", "colorama")]:
        try:
            importlib.import_module(mod)
        except ImportError:
            print(f"[*] Menginstal paket '{pkg}'...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", pkg, "-q",
                "--break-system-packages"
            ])

ensure_deps()

import qrcode                           # type: ignore
import qrcode.constants                 # type: ignore
from colorama import init, Fore, Style  # type: ignore

init(autoreset=True)

# ── Constants ─────────────────────────────────────────────────────────────────
DB_PATH   = Path("wifi.db")
JSON_PATH = Path("wifi.json")
CHARS     = string.ascii_letters + string.digits
BULAN_ID  = [
    "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

def SEP(color=Fore.CYAN):
    return color + "─" * 52 + Style.RESET_ALL

# ── Time utilities ────────────────────────────────────────────────────────────
def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def expiry_from_days(days: int) -> str:
    return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

def fmt_tanggal(dt_str: str) -> str:
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    return f"{dt.day}-{BULAN_ID[dt.month]}-{dt.year}"

def generate_password(length: int = 12) -> str:
    return "".join(random.choices(CHARS, k=length))

# ── WiFi URI & QR ─────────────────────────────────────────────────────────────
def wifi_uri(ssid: str, password: str, auth: str = "WPA") -> str:
    def esc(s):
        return s.replace("\\", "\\\\").replace(";", "\\;") \
                .replace(",", "\\,").replace('"', '\\"')
    return f"WIFI:T:{auth};S:{esc(ssid)};P:{esc(password)};;"

def print_qr(data: str):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=1,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    print()
    for row in qr.get_matrix():
        print(Fore.WHITE + "".join("██" if cell else "  " for cell in row))
    print()

# ══════════════════════════════════════════════════════════════════════════════
# DATABASE — SQLite
# ══════════════════════════════════════════════════════════════════════════════
def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pelanggan (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                customer    TEXT    NOT NULL,
                ssid        TEXT    NOT NULL,
                password    TEXT    NOT NULL,
                duration    INTEGER NOT NULL,
                start_time  TEXT    NOT NULL,
                expiry_time TEXT    NOT NULL
            )
        """)

# ── JSON → SQLite migration ──────────────────────────────────────────────────────
def migrate_from_json():
    """
    Jika wifi.json ditemukan:
      1. Baca semua entri
      2. Insert ke SQLite (hanya jika DB masih kosong)
      3. Rename wifi.json → wifi.json.migrated (data asli tetap aman)
    """
    if not JSON_PATH.exists():
        return

    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        print(Fore.RED + "[!] Failed to read wifi.json — migration skipped.")
        return

    if not isinstance(data, list) or len(data) == 0:
        JSON_PATH.rename(JSON_PATH.with_suffix(".json.migrated"))
        return

    with get_conn() as conn:
        total_db = conn.execute("SELECT COUNT(*) FROM pelanggan").fetchone()[0]
        if total_db > 0:
            print(Fore.YELLOW +
                  f"[!] Database already contains {total_db} entries. "
                  "Delete wifi.db first if you want to re-migrate.")
            return

        inserted = 0
        skipped  = 0
        required = {"customer", "ssid", "password", "duration", "start_time", "expiry_time"}

        for row in data:
            if not required.issubset(row.keys()):
                skipped += 1
                continue
            conn.execute("""
                INSERT INTO pelanggan
                    (customer, ssid, password, duration, start_time, expiry_time)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                row["customer"], row["ssid"], row["password"],
                int(row["duration"]), row["start_time"], row["expiry_time"]
            ))
            inserted += 1

    migrated_path = JSON_PATH.with_name("wifi.json.migrated")
    JSON_PATH.rename(migrated_path)

    print()
    print(SEP(Fore.GREEN))
    print(Fore.GREEN + "  [✓] MIGRATION SUCCESSFUL")
    print(Fore.GREEN + f"      {inserted} entries migrated from wifi.json → wifi.db")
    if skipped:
        print(Fore.YELLOW + f"      {skipped} entries skipped (incomplete fields)")
    print(Fore.GREEN + f"      File asli aman di: {migrated_path.name}")
    print(SEP(Fore.GREEN))
    input(Fore.WHITE + "\n  Press Enter to continue..." + Style.RESET_ALL)

# ── CRUD ───────────────────────────────────────────────────────────────────────
def db_insert(customer, ssid, password, duration, start_time, expiry_time):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO pelanggan
                (customer, ssid, password, duration, start_time, expiry_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (customer, ssid, password, duration, start_time, expiry_time))

def db_all():
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM pelanggan ORDER BY expiry_time DESC"
        ).fetchall()

def db_active():
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM pelanggan WHERE expiry_time > ? ORDER BY expiry_time ASC",
            (now_str(),)
        ).fetchall()

def db_expired():
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM pelanggan WHERE expiry_time <= ? ORDER BY expiry_time DESC",
            (now_str(),)
        ).fetchall()

def db_delete(row_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM pelanggan WHERE id = ?", (row_id,))

# ══════════════════════════════════════════════════════════════════════════════
# DISPLAY
# ══════════════════════════════════════════════════════════════════════════════
def print_entry(e, show_qr: bool = True):
    uri = wifi_uri(e["ssid"], e["password"])
    print(Fore.CYAN  + "  Nama            : " + Fore.WHITE + e["customer"])
    print(Fore.CYAN  + "  SSID            : " + Fore.WHITE + e["ssid"])
    print(Fore.CYAN  + "  Password        : " + Fore.WHITE + e["password"])
    print(Fore.CYAN  + "  Waktu aktif     : " + Fore.WHITE + f"{e['duration']} hari")
    print(Fore.CYAN  + "  Tanggal berakhir: " + Fore.WHITE + fmt_tanggal(e["expiry_time"]))
    if show_qr:
        print(Fore.YELLOW + "  Scan QR to connect directly to WiFi:")
        print_qr(uri)

# ── Menu 1: Add ────────────────────────────────────────────────────────────────
def add_entry():
    print(SEP())
    print(Fore.YELLOW + "  ✚  Add New WiFi Customer")
    print(SEP())

    nama = input(Fore.GREEN + "Customer name: " + Style.RESET_ALL).strip()
    if not nama:
        print(Fore.RED + "[!] Name cannot be empty.")
        return

    ssid_default = nama.replace(" ", "_")
    ssid = input(
        Fore.GREEN + f"SSID           [{ssid_default}]: " + Style.RESET_ALL
    ).strip() or ssid_default

    try:
        duration = int(input(Fore.GREEN + "Durasi (hari)  : " + Style.RESET_ALL))
        if duration <= 0:
            raise ValueError
    except ValueError:
        print(Fore.RED + "[!] Durasi harus bilangan bulat positif.")
        return

    password   = generate_password()
    start_time = now_str()
    expiry     = expiry_from_days(duration)

    db_insert(nama, ssid, password, duration, start_time, expiry)

    print()
    print(SEP())
    entry = {"customer": nama, "ssid": ssid, "password": password,
             "duration": duration, "expiry_time": expiry}
    print_entry(entry, show_qr=True)
    print(SEP())

# ── Menu 2: Active list ────────────────────────────────────────────────────────
def list_active():
    rows = db_active()
    print(SEP())
    print(Fore.YELLOW + f"  Active Customers  ({len(rows)} entries)")
    print(SEP())
    if not rows:
        print(Fore.RED + "  No active customers at the moment.")
        return
    for e in rows:
        print_entry(e, show_qr=True)
        print(SEP())

# ── Menu 3: Expired list ──────────────────────────────────────────────────────
def list_expired():
    # use print_entry so QR code is displayed
    rows = db_expired()
    print(SEP())
    print(Fore.YELLOW + f"  Expired Customers  ({len(rows)} entries)")
    print(SEP())
    if not rows:
        print(Fore.GREEN + "  No expired customers.")
        return
    for e in rows:
        print_entry(e, show_qr=True)
        print(SEP(Fore.RED))

# ── Menu 4: Delete ─────────────────────────────────────────────────────────────
def delete_entry():
    rows = db_all()
    if not rows:
        print(Fore.RED + "  Database kosong.")
        return

    print(SEP())
    print(Fore.YELLOW + "  Delete Customer")
    print(SEP())

    now = now_str()
    for i, e in enumerate(rows, 1):
        status = (Fore.GREEN + "Aktif  ") if e["expiry_time"] > now else (Fore.RED + "Expired")
        print(f"  {Fore.WHITE}{i:>3}. {e['customer']:<28} {status}{Style.RESET_ALL}  [{e['ssid']}]")

    try:
        idx = int(input(Fore.GREEN + "\nNumber to delete (0=cancel): " + Style.RESET_ALL))
        if idx == 0:
            return
        if not (1 <= idx <= len(rows)):
            raise ValueError
    except ValueError:
        print(Fore.RED + "[!] Invalid choice.")
        return

    target = rows[idx - 1]
    konfirmasi = input(
        Fore.YELLOW + f"  Delete '{target['customer']}'? (y/N): " + Style.RESET_ALL
    ).strip().lower()
    if konfirmasi != "y":
        print("  Cancelled.")
        return

    db_delete(target["id"])
    print(Fore.GREEN + f"  [✓] Customer '{target['customer']}' successfully deleted.")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    init_db()
    migrate_from_json()   # ← runs automatically if wifi.json is found

    MENU = f"""
{Fore.CYAN}╔══════════════════════════════╗
║   WiFi Credential Manager   ║
║        SQLite Edition       ║
╚══════════════════════════════╝{Style.RESET_ALL}
  {Fore.WHITE}1.{Style.RESET_ALL} Tambah pelanggan baru
  {Fore.WHITE}2.{Style.RESET_ALL} Daftar pelanggan aktif
  {Fore.WHITE}3.{Style.RESET_ALL} Daftar pelanggan expired
  {Fore.WHITE}4.{Style.RESET_ALL} Hapus pelanggan
  {Fore.WHITE}5.{Style.RESET_ALL} Keluar
"""

    while True:
        print(MENU)
        choice = input(Fore.YELLOW + "Choice: " + Style.RESET_ALL).strip()

        if choice == "1":
            add_entry()
        elif choice == "2":
            list_active()
        elif choice == "3":
            list_expired()
        elif choice == "4":
            delete_entry()
        elif choice in ("5", "q", "exit"):
            print(Fore.CYAN + "\n  Terima kasih. Program ditutup.\n")
            break
        else:
            print(Fore.RED + "  [!] Invalid choice.")

if __name__ == "__main__":
    main()
