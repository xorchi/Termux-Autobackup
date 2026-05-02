#!/usr/bin/env bash
# =============================================================================
#  xmr — Monero wallet launcher with GPG-encrypted vault
#  Final version — merged best of all three versions
# =============================================================================
set -euo pipefail

# ─── Paths ────────────────────────────────────────────────────────────────────

VAULT_SRC="/data/data/com.termux/files/usr/var/vault"
WORKDIR="$HOME/Termux-Autobackup/xmr"

# ─── Logging helpers ──────────────────────────────────────────────────────────

_log()   { printf '[%s] +     %s\n' "$(date '+%H:%M:%S')" "$*"; }
_warn()  { printf '[%s] WARN  %s\n' "$(date '+%H:%M:%S')" "$*" >&2; }
_fatal() { printf '[%s] FATAL %s\n' "$(date '+%H:%M:%S')" "$*" >&2; exit 1; }

# ─── Trap / cleanup ───────────────────────────────────────────────────────────

_ENCRYPTED=0

_cleanup() {
    if [[ $_ENCRYPTED -eq 0 ]]; then
        _warn "Script exited before encryption. Cleaning up plaintext wallet..."
        rm -f "$WORKDIR/${WALLET_NAME:-}" "$WORKDIR/${WALLET_NAME:-}.keys"
    fi
}

trap '_cleanup' EXIT
trap 'exit 1'   INT TERM

# ─── Load & validate config ───────────────────────────────────────────────────

[[ -f "$VAULT_SRC/config" ]] \
    || _fatal "Config file not found at $VAULT_SRC/config."

# shellcheck source=/dev/null
source "$VAULT_SRC/config"

for _var in WALLET_NAME GPG_RECIPIENT NODE_CLEARNET NODE_ONION; do
    [[ -n "${!_var:-}" ]] || _fatal "Config variable \$$_var is missing or empty."
done

WALLET_FILE="$WORKDIR/$WALLET_NAME"
MONERO_BIN=$(command -v monero-wallet-cli || true)

# ─── Leftover check ───────────────────────────────────────────────────────────

if [[ -f "$WALLET_FILE" || -f "$WALLET_FILE.keys" ]]; then
    _warn "Leftover plaintext wallet from a previous session found. Removing..."
    rm -f "$WALLET_FILE" "$WALLET_FILE.keys"
fi

# ─── Functions ────────────────────────────────────────────────────────────────

_check_monero() {
    [[ -n "$MONERO_BIN" ]] && return 0

    _warn "monero-wallet-cli not found."
    read -rp "Install now? (y/n) " _yn
    [[ "$_yn" == "y" ]] || _fatal "monero-wallet-cli required. Aborting."

    pkg install monero -y
    MONERO_BIN=$(command -v monero-wallet-cli || true)
    [[ -n "$MONERO_BIN" ]] || _fatal "Installation failed. monero-wallet-cli still not found."
}

# Validasi file vault sebelum dekripsi
_check_vault_files() {
    [[ -f "$VAULT_SRC/$WALLET_NAME.gpg" ]]      || _fatal "Vault file not found: $VAULT_SRC/$WALLET_NAME.gpg"
    [[ -f "$VAULT_SRC/$WALLET_NAME.keys.gpg" ]] || _fatal "Vault file not found: $VAULT_SRC/$WALLET_NAME.keys.gpg"
}

_gpg_decrypt_pair() {
    gpg --yes -d -o "$WALLET_FILE"      "$VAULT_SRC/$WALLET_NAME.gpg"
    gpg --yes -d -o "$WALLET_FILE.keys" "$VAULT_SRC/$WALLET_NAME.keys.gpg"
}

_gpg_fix_agent() {
    local gpgdir="$HOME/.gnupg"
    gpgconf --kill gpg-agent                              || true
    rm -f "$gpgdir"/*.lock "$gpgdir"/.#lock* 2>/dev/null || true
    chmod 700 "$gpgdir"                   2>/dev/null     || true
    gpgconf --launch gpg-agent                            || true
    sleep 0.5
}

decrypt() {
    _check_vault_files
    mkdir -p "$WORKDIR"

    local attempt
    for attempt in 1 2; do
        if _gpg_decrypt_pair; then
            return 0
        fi
        _warn "Decrypt attempt $attempt failed."
        if [[ $attempt -eq 1 ]]; then
            _log "Attempting GPG agent repair..."
            _gpg_fix_agent
        fi
    done

    _fatal "Decryption failed after retries. Check your GPG key or passphrase."
}

# Atomic encrypt: tulis ke .tmp dulu, baru mv — vault tidak corrupt jika gagal
encrypt() {
    local opts=(--batch --yes --trust-model always --encrypt --recipient "$GPG_RECIPIENT")
    local tmp1="$VAULT_SRC/$WALLET_NAME.gpg.tmp"
    local tmp2="$VAULT_SRC/$WALLET_NAME.keys.gpg.tmp"

    gpg "${opts[@]}" -o "$tmp1" "$WALLET_FILE"      || { rm -f "$tmp1" "$tmp2"; _fatal "Encryption failed (wallet)."; }
    gpg "${opts[@]}" -o "$tmp2" "$WALLET_FILE.keys" || { rm -f "$tmp1" "$tmp2"; _fatal "Encryption failed (keys)."; }

    mv -f "$tmp1" "$VAULT_SRC/$WALLET_NAME.gpg"
    mv -f "$tmp2" "$VAULT_SRC/$WALLET_NAME.keys.gpg"

    _ENCRYPTED=1
    _log "Wallet re-encrypted to vault."
}

# ─── Tor readiness check ──────────────────────────────────────────────────────

_tor_ready() {
    local tor_log="$HOME/.local/share/tor/log.txt"

    # Method 1: bootstrap log
    if [[ -f "$tor_log" ]] && grep -q "Bootstrapped 100%" "$tor_log" 2>/dev/null; then
        return 0
    fi

    # Method 2: TCP probe via /dev/tcp (bash built-in)
    if { echo > /dev/tcp/127.0.0.1/9050; } 2>/dev/null \
    || { echo > /dev/tcp/127.0.0.1/9150; } 2>/dev/null; then
        return 0
    fi

    # Method 3: netcat fallback
    if command -v nc >/dev/null 2>&1; then
        nc -z 127.0.0.1 9050 2>/dev/null || nc -z 127.0.0.1 9150 2>/dev/null && return 0
    fi

    return 1
}

_run_tor() {
    local base_opts=("$@")
    local tor_log="$HOME/.local/share/tor/log.txt"
    local timeout=60

    command -v tor >/dev/null 2>&1 || _fatal "tor: not installed. Run: pkg install tor"

    mkdir -p "$(dirname "$tor_log")"

    if ! pgrep -x tor >/dev/null 2>&1; then
        truncate -s 0 "$tor_log" 2>/dev/null || true
        tor > "$tor_log" 2>&1 &
        _log "Tor started (PID $!). Waiting for bootstrap..."
    else
        _log "Tor already running. Waiting for readiness..."
    fi

    local tor_opts=(
        "${base_opts[@]}"
        "--daemon-address" "$NODE_ONION"
        "--proxy"          "127.0.0.1:9050"
        "--trusted-daemon"
    )

    local i=0
    while [[ $i -lt $timeout ]]; do
        if _tor_ready; then
            _log "Tor is ready. Launching wallet..."
            "$MONERO_BIN" "${tor_opts[@]}"
            return
        fi
        sleep 1
        i=$((i+1))
    done

    _fatal "Tor bootstrap timed out after ${timeout}s."
}

# ─── Monero launcher ──────────────────────────────────────────────────────────

run_monero() {
    local mode="$1"
    local base_opts=(
        "--wallet-file" "$WALLET_FILE"
        "--log-file"    "/dev/null"
        "--log-level"   "0"
    )

    case "$mode" in
        clearnet)
            _log "Connecting via clearnet: $NODE_CLEARNET"
            "$MONERO_BIN" "${base_opts[@]}" \
                --daemon-address "$NODE_CLEARNET" \
                --trusted-daemon
            ;;
        offline)
            _log "Running in offline mode."
            "$MONERO_BIN" "${base_opts[@]}" --offline
            ;;
        tor)
            _run_tor "${base_opts[@]}"
            ;;
    esac
}

# ─── Usage ────────────────────────────────────────────────────────────────────

_usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTION]

Run monero-wallet-cli with encrypted wallet via vault.

Options:
  -c, --clearnet   Connect using clearnet node
  -o, --offline    Run in offline mode (no sync)
  -h, --help       Show this help message

Default (no flag): Connect via Tor (onion node)
EOF
    exit 0
}

# ─── Main ─────────────────────────────────────────────────────────────────────

MODE="tor"

case "${1:-}" in
    -c|--clearnet) MODE="clearnet" ;;
    -o|--offline)  MODE="offline"  ;;
    -h|--help)     _usage          ;;
    "")            ;;
    *) _warn "Unknown flag: ${1}"; _usage ;;
esac

_check_monero

if [[ ! -f "$WALLET_FILE" || ! -f "$WALLET_FILE.keys" ]]; then
    _log "Decrypting wallet from vault..."
    decrypt
fi

run_monero "$MODE"

encrypt

trap - EXIT INT TERM
rm -f "$WALLET_FILE" "$WALLET_FILE.keys"
_log "Done. Plaintext wallet cleared."

