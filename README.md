# Termux-Autobackup

> 🇮🇩 [Baca dalam Bahasa Indonesia](README.id.md)

A personal utility repository for Termux — a collection of scripts and tools for backup, system management, WiFi credential management, Monero wallet handling, and various small utilities.

---

## Installation

```bash
pkg install git
git clone https://github.com/xorchi/Termux-Autobackup
cd Termux-Autobackup
cp others/config.example others/config
# Edit others/config and fill in your values
```

---

## Structure

```
Termux-Autobackup/
├── xmr/
│   ├── main.sh           # Monero wallet manager (GPG-encrypted)
│   └── vault/            # Runtime only — excluded from git
│       └── config        # Wallet config (name, GPG recipient, nodes)
├── utils/
│   ├── backup.sh         # Full Termux backup to /sdcard
│   ├── restore.sh        # Restore Termux from backup archive
│   ├── cloud-server.sh   # FileBrowser + Cloudflare tunnel server
│   ├── enc.sh            # GPG encrypt a file
│   ├── dec.sh            # GPG decrypt a file
│   ├── xmr-nodes.sh      # Fetch available Monero nodes
│   ├── fng.sh            # Crypto Fear & Greed Index
│   ├── random.sh         # Random number generator (lottery format)
│   ├── repo-list.sh      # List GitHub repos by star count
│   ├── main-repo.sh      # Reset Termux package repository to official
│   ├── bip39             # BIP39 seed phrase generator (binary)
│   ├── pass.py           # Secure password generator
│   ├── username.py       # Anonymous username generator
│   ├── gainer-loser.py   # Crypto top gainer/loser tracker
│   ├── largest.py        # Find largest files in Termux directory
│   ├── 100.py            # Top 100 crypto by market cap
│   └── exc.py            # XMR/USD/IDR price & currency converter
├── wifi/
│   └── wifi_manager.py   # WiFi credential manager (SQLite)
├── others/
│   ├── config.example    # Global config template
│   ├── dns.txt           # DNS server list
│   └── gpg-pubkey.asc    # GPG public key for commit verification
└── store/
    └── index.html        # Local store page
```

---

## Requirements

Install these packages before using scripts that depend on them:

```bash
pkg install git gpg python tor monero
pip install requests colorama pycoingecko --break-system-packages
```

For cloud server:
```bash
pkg install cloudflared
pip install qrcode --break-system-packages
# filebrowser: install manually from https://filebrowser.org
```

For GitHub tools:
```bash
pkg install gh
```

---

## Configuration

Copy the example config and fill in your values before first use:

```bash
cp others/config.example others/config
```

`others/config` is excluded from git. Contents:

```bash
GPG_RECIPIENT=""       # Your GPG key name or fingerprint
CLOUD_PORT=""          # Port for FileBrowser (default: 8080)
CLOUD_STORAGE=""       # Directory to expose (default: /sdcard)
GITHUB_USERNAME=""     # Your GitHub username
```

---

## Monero Wallet (`xmr/main.sh`)

A hardened Monero CLI wallet wrapper with GPG encryption at rest.

**Features:**
- Wallet files are GPG-encrypted when not in use
- Supports Tor, clearnet, and offline modes
- Auto-cleanup on abnormal exit (SIGINT, SIGTERM)
- Detects and cleans up leftover plaintext files from previous crashed sessions
- Config-driven (no hardcoded wallet names or node addresses)

**Requirements:** `monero-wallet-cli`, `gpg`, `tor` (Tor mode only)

The `vault/` directory lives permanently at `$PREFIX/var/vault/` and is copied to `xmr/vault/` only during runtime.

Create this file manually before first run.

**Config** (`$PREFIX/var/vault/config`):
```bash
WALLET_NAME="your_wallet_name"
GPG_RECIPIENT="YOUR_GPG_KEY_FINGERPRINT"
NODE_CLEARNET="host:port"
NODE_ONION="host.onion:port"
```

**Usage:**
```bash
bash xmr/main.sh
# Then select:
# 1 = Tor
# 2 = Clearnet
# 3 = Offline
```

---

## Backup & Restore

Full Termux environment backup and restore to/from `/sdcard`.

```bash
# Full backup
bash utils/backup.sh

# Restore from archive
bash utils/restore.sh /sdcard/termux_backup_YYYYMMDD_HHMM.tar.gz
```

---

## Cloud Server

Exposes `/sdcard` via FileBrowser over a Cloudflare tunnel. Displays a QR code in terminal when ready. Requires `CLOUD_PORT` and `CLOUD_STORAGE` in `others/config`.

```bash
bash utils/cloud-server.sh
```

**Requirements:** `filebrowser`, `cloudflared`, `python3`, `qrcode`

---

## WiFi Manager

SQLite-backed WiFi credential manager with QR code generation for easy sharing.

```bash
cd wifi && python3 wifi_manager.py
```

---

## Crypto Utilities

**Top gainer/loser tracker** — shows top 10 gainers and losers from the top 250 coins by market cap, with 1h/24h/7d/30d change. Filters out coins below $10M market cap.
```bash
python3 utils/gainer-loser.py
```

**Top 100 by market cap** — displays top 100 coins with price and 30d change.
```bash
python3 utils/100.py
```

**XMR price & converter** — fetches live XMR price in USD and IDR, with interactive currency conversion menu (XMR/USD/IDR).
```bash
python3 utils/exc.py
```

**Fear & Greed Index** — fetches current crypto Fear & Greed Index from alternative.me.
```bash
bash utils/fng.sh
```

**Monero node list** — fetches list of active Monero nodes from monero.fail.
```bash
bash utils/xmr-nodes.sh
```

---

## System Utilities

**GPG encrypt/decrypt** — encrypt or decrypt any file using the GPG recipient set in `others/config`.
```bash
bash utils/enc.sh
bash utils/dec.sh
```

**Password generator** — generates a cryptographically secure password using the full printable character set.
```bash
python3 utils/pass.py          # default 44 chars
python3 utils/pass.py -l 128   # custom length
```

**Username generator** — generates a random anonymous username from BIP39 wordlist.
```bash
python3 utils/username.py
```

**BIP39 seed phrase generator** — generates a BIP39-compatible mnemonic seed phrase.
```bash
./utils/bip39
```

**Find largest files** — scans the Termux directory and lists the top 10 largest files.
```bash
python3 utils/largest.py
```

**Random number generator** — generates random numbers in lottery format (2D to 6D).
```bash
bash utils/random.sh
```

**GitHub repo list** — lists your GitHub repositories sorted by star count. Requires `GITHUB_USERNAME` in `others/config` and `gh` CLI authenticated.
```bash
bash utils/repo-list.sh
```

**Reset Termux repository** — resets `sources.list` to the official Termux package repository.
```bash
bash utils/main-repo.sh
```

---

## GPG Public Key

The file `others/gpg-pubkey.asc` contains the GPG public key used to sign all commits in this repository. You can import it to verify commit signatures:

```bash
gpg --import others/gpg-pubkey.asc
git log --show-signature
```

---

## Notes

- All commits are GPG-signed.
- Sensitive files (`xmr/vault/`, `*.gpg`, `*.db`, `others/config`) are excluded via `.gitignore`.
- This repository is intended for personal use. Adapt paths and configurations to your own environment before use.
