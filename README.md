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
│   ├── local-cloud.sh    # FileBrowser on local network (no Cloudflare)
│   ├── install-debian.sh # Automated proot-distro Debian setup with zsh + zinit
│   ├── enc.sh            # GPG encrypt a file
│   ├── dec.sh            # GPG decrypt a file
│   ├── git-remote.sh     # Auto-configure git identity per repo based on SSH remote
│   ├── wa-gojek.sh       # GoSend WhatsApp confirmation message generator
│   ├── webserver.sh      # Local web server launcher for host/ subdirectories
│   ├── xmr-nodes.sh      # Fetch available Monero nodes
│   ├── fng.sh            # Crypto Fear & Greed Index
│   ├── random.sh         # Random number generator (lottery format)
│   ├── repo-list.sh      # List GitHub repos by star count
│   ├── main-repo.sh      # Reset Termux package repository to official
│   ├── bip39             # BIP39 seed phrase generator (binary)
│   ├── bip39cli.py       # BIP39/Monero mnemonic tool — generate, validate, derive addresses (BTC/ETH/BNB/SOL/XMR), convert BIP39 to Monero seed
│   ├── polyseed.py       # Polyseed 16-word to Monero 25-word seed converter with passphrase support
│   ├── generate_segwit_address.py  # BIP84 SegWit address generator from zpub
│   ├── btc-cycle.py      # Bitcoin halving cycle projection — bottom/ATH estimation with weighted log regression
│   ├── btc_data.json     # Historical BTC cycle data (tops and bottoms) for btc-cycle.py
│   ├── ema.py            # EMA 200 daily screener for top 100 coins via Binance API
│   ├── xmr_supply_calculator.py  # Deterministic XMR circulating supply calculator
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
└── host/                 # Self-hosting directory — contents excluded from git
    └── index.html        # Hosted page (served via Tor hidden service / I2P eepsite)
```

---

## Requirements

Install these packages before using scripts that depend on them:

```bash
pkg install git gpg python tor i2pd monero
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
CLOUD_PORT=""          # Port for FileBrowser cloud server (default: 8080)
CLOUD_STORAGE=""       # Directory to expose via cloud server (default: /sdcard)
LOCAL_PORT=""          # Port for local FileBrowser server
LOCAL_STORAGE=""       # Directory to expose via local server
LOCAL_GATEWAY=""       # Local gateway IP (e.g. 192.168.1.1) for IP detection
GITHUB_USERNAME=""     # Your GitHub username
PROFILE1_HOST=""       # SSH host for git profile 1 (e.g. github.com)
PROFILE1_NAME=""       # Git user.name for profile 1
PROFILE1_EMAIL=""      # Git user.email for profile 1
PROFILE1_GPG=""        # GPG signing key for profile 1
# Additional profiles: PROFILE2_*, PROFILE3_*, etc.
```

---

## Monero Wallet (`xmr/main.sh`)

A hardened Monero CLI wallet wrapper with GPG encryption at rest.

**Features:**
- Wallet files are GPG-encrypted when not in use
- Supports Tor, clearnet, I2P, and offline modes
- Auto-cleanup on abnormal exit (SIGINT, SIGTERM)
- Detects and cleans up leftover plaintext files from previous crashed sessions
- Config-driven (no hardcoded wallet names or node addresses)

**Requirements:** `monero-wallet-cli`, `gpg`, `tor` (Tor mode only), `i2pd` (I2P mode only)

The `vault/` directory lives permanently at `$PREFIX/var/vault/` and is copied to `xmr/vault/` only during runtime.

Create this file manually before first run.

**Config** (`$PREFIX/var/vault/config`):
```bash
WALLET_NAME="your_wallet_name"
GPG_RECIPIENT="YOUR_GPG_KEY_FINGERPRINT"
NODE_CLEARNET="host:port"
NODE_ONION="host.onion:port"
NODE_I2P="host.b32.i2p:port"
```

**Usage:**
```bash
xmr        # Default: Tor
xmr -c     # Clearnet
xmr -i     # I2P
xmr -o     # Offline
xmr -h     # Help
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

Exposes a directory via FileBrowser over a Cloudflare tunnel. Displays a QR code in terminal when ready. Requires `CLOUD_PORT` and `CLOUD_STORAGE` in `others/config`.

```bash
bash utils/cloud-server.sh
```

**Requirements:** `filebrowser`, `cloudflared`, `python3`, `qrcode`

For local network access without Cloudflare, use `local-cloud.sh` instead. Requires `LOCAL_PORT`, `LOCAL_STORAGE`, and `LOCAL_GATEWAY` in `others/config`.

```bash
bash utils/local-cloud.sh
```

---

## WiFi Manager

SQLite-backed WiFi credential manager with QR code generation for easy sharing.

```bash
cd wifi && python3 wifi_manager.py
```

---

## Crypto Utilities

**BIP39/Monero mnemonic tool** — interactive and CLI tool. Generate BIP39 or Monero 25-word seeds, validate, derive addresses (BTC all types, ETH, BNB, SOL, XMR), convert BIP39 to Monero seed, apply Monero native offset passphrase. Zero dependency, stdlib only.
```bash
python3 utils/bip39cli.py                          # interactive
python3 utils/bip39cli.py generate 24
python3 utils/bip39cli.py generate --xmr
python3 utils/bip39cli.py derive "<mnemonic>" "" --coin btc
python3 utils/bip39cli.py --help
```

**Polyseed converter** — converts a 16-word Polyseed mnemonic (with optional passphrase) to a Monero 25-word seed and primary address. Includes self-test against known test vectors. Zero dependency, stdlib only.
```bash
python3 utils/polyseed.py
```

**SegWit address generator** — derives BIP84 native SegWit addresses from a zpub. Supports change/receive chains and custom index ranges.
```bash
python3 utils/generate_segwit_address.py <zpub> --count 10
```

**Bitcoin cycle projection** — projects the next BTC cycle bottom and ATH using weighted log regression on historical halving cycles. Data stored in `btc_data.json`, editable via interactive menu. Zero dependency, stdlib only.
```bash
python3 utils/btc-cycle.py
```

**EMA 200 daily screener** — screens top 100 coins by volume on Binance and lists those with closing price above EMA 200, sorted by proximity to the EMA.
```bash
python3 utils/ema.py
```

**XMR supply calculator** — deterministically calculates total XMR in circulation by simulating every block from genesis using Monero's official emission formula. Fetches block height from a public API; all supply math is local.
```bash
python3 utils/xmr_supply_calculator.py
python3 utils/xmr_supply_calculator.py --verbose
```

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

**Git remote configurator** — auto-detects the SSH remote URL of the current repo and applies the matching git identity (name, email, GPG key) from `others/config`. Falls back to a manual profile menu if no match is found.
```bash
bash utils/git-remote.sh
```

**GoSend WhatsApp tool** — generates pickup or dropoff confirmation messages for GoSend deliveries and opens them directly in WhatsApp. Driver name is read from `PROFILE2_NAME` in `others/config`.
```bash
bash utils/wa-gojek.sh
```
**Web server launcher** — starts a local HTTP server on port 8080 for a named subdirectory inside `host/`. Lists available directories when called without arguments.
```bash
bash utils/webserver.sh toko
bash utils/webserver.sh   # list available
```
**Debian installer** — automated setup of proot-distro Debian Trixie with zsh, zinit, plugins (autosuggestions, syntax-highlighting, fzf-tab), neovim, eza, and a custom osx2 theme.
```bash
bash utils/install-debian.sh
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

## Self-Hosting (`host/`)

The `host/` directory is intended for files served via Tor hidden service or I2P eepsite. Its contents are excluded from git — the directory is visible in the repository but its files are private.

Configure Tor and i2pd to point to a local server (e.g. `python3 -m http.server 8080`) serving this directory.

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
- Sensitive files (`xmr/vault/`, `*.gpg`, `*.db`, `others/config`, `host/*`) are excluded via `.gitignore`.
- This repository is intended for personal use. Adapt paths and configurations to your own environment before use.

