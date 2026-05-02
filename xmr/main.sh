#!/usr/bin/env bash
# xmr — Monero wallet launcher with GPG-encrypted vault
set -euo pipefail

VAULT_SRC="/data/data/com.termux/files/usr/var/vault"
WORKDIR="$HOME/Termux-Autobackup/xmr"

_warn()  { echo "[WARN]  $*" >&2; }
_fatal() { echo "[FATAL] $*" >&2; exit 1; }

_ENCRYPTED=0

_cleanup() {
    if [[ $_ENCRYPTED -eq 0 ]]; then
        _warn "Exited before encryption. Removing plaintext wallet."
        rm -f "$WORKDIR/${WALLET_NAME:-}" "$WORKDIR/${WALLET_NAME:-}.keys"
    fi
}

trap '_cleanup' EXIT
trap 'exit 1'   INT TERM

[[ -f "$VAULT_SRC/config" ]] || _fatal "Config not found: $VAULT_SRC/config"

# shellcheck source=/dev/null
source "$VAULT_SRC/config"

for _var in WALLET_NAME GPG_RECIPIENT NODE_CLEARNET NODE_ONION; do
    [[ -n "${!_var:-}" ]] || _fatal "Config variable \$$_var is missing or empty."
done

WALLET_FILE="$WORKDIR/$WALLET_NAME"
MONERO_BIN=$(command -v monero-wallet-cli || true)

if [[ -f "$WALLET_FILE" || -f "$WALLET_FILE.keys" ]]; then
    _warn "Leftover plaintext wallet found. Removing."
    rm -f "$WALLET_FILE" "$WALLET_FILE.keys"
fi

_check_monero() {
    [[ -n "$MONERO_BIN" ]] && return 0
    _warn "monero-wallet-cli not found."
    read -rp "Install now? (y/n) " _yn
    [[ "$_yn" == "y" ]] || _fatal "monero-wallet-cli required."
    pkg install monero -y
    MONERO_BIN=$(command -v monero-wallet-cli || true)
    [[ -n "$MONERO_BIN" ]] || _fatal "Installation failed."
}

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
        _gpg_decrypt_pair && return 0
        _warn "Decrypt attempt $attempt failed."
        [[ $attempt -eq 1 ]] && _gpg_fix_agent
    done
    _fatal "Decryption failed after retries."
}

encrypt() {
    local opts=(--batch --yes --trust-model always --encrypt --recipient "$GPG_RECIPIENT")
    local tmp1="$VAULT_SRC/$WALLET_NAME.gpg.tmp"
    local tmp2="$VAULT_SRC/$WALLET_NAME.keys.gpg.tmp"
    gpg "${opts[@]}" -o "$tmp1" "$WALLET_FILE"      || { rm -f "$tmp1" "$tmp2"; _fatal "Encryption failed (wallet)."; }
    gpg "${opts[@]}" -o "$tmp2" "$WALLET_FILE.keys" || { rm -f "$tmp1" "$tmp2"; _fatal "Encryption failed (keys)."; }
    mv -f "$tmp1" "$VAULT_SRC/$WALLET_NAME.gpg"
    mv -f "$tmp2" "$VAULT_SRC/$WALLET_NAME.keys.gpg"
    _ENCRYPTED=1
}

_tor_ready() {
    local tor_log="$HOME/.local/share/tor/log.txt"
    [[ -f "$tor_log" ]] && grep -q "Bootstrapped 100%" "$tor_log" 2>/dev/null && return 0
    { echo > /dev/tcp/127.0.0.1/9050; } 2>/dev/null && return 0
    { echo > /dev/tcp/127.0.0.1/9150; } 2>/dev/null && return 0
    if command -v nc >/dev/null 2>&1; then
        nc -z 127.0.0.1 9050 2>/dev/null && return 0
        nc -z 127.0.0.1 9150 2>/dev/null && return 0
    fi
    return 1
}

_run_tor() {
    local base_opts=("$@")
    local tor_log="$HOME/.local/share/tor/log.txt"
    local timeout=60

    command -v tor >/dev/null 2>&1 || _fatal "tor not installed. Run: pkg install tor"

    mkdir -p "$(dirname "$tor_log")"
    if ! pgrep -x tor >/dev/null 2>&1; then
        truncate -s 0 "$tor_log" 2>/dev/null || true
        tor > "$tor_log" 2>&1 &
    fi

    local i=0
    while [[ $i -lt $timeout ]]; do
        if _tor_ready; then
            "$MONERO_BIN" "${base_opts[@]}" \
                --daemon-address "$NODE_ONION" \
                --proxy          "127.0.0.1:9050" \
                --trusted-daemon
            return
        fi
        sleep 1
        i=$((i+1))
    done

    _fatal "Tor bootstrap timed out after ${timeout}s."
}

run_monero() {
    local base_opts=(
        "--wallet-file" "$WALLET_FILE"
        "--log-file"    "/dev/null"
        "--log-level"   "0"
    )
    case "$1" in
        clearnet)
            "$MONERO_BIN" "${base_opts[@]}" --daemon-address "$NODE_CLEARNET" --trusted-daemon ;;
        offline)
            "$MONERO_BIN" "${base_opts[@]}" --offline ;;
        tor)
            _run_tor "${base_opts[@]}" ;;
    esac
}

_usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTION]

Options:
  -c, --clearnet   Connect via clearnet node
  -o, --offline    Run in offline mode
  -h, --help       Show this help

Default: Connect via Tor (onion node)
EOF
    exit 0
}

MODE="tor"
case "${1:-}" in
    -c|--clearnet) MODE="clearnet" ;;
    -o|--offline)  MODE="offline"  ;;
    -h|--help)     _usage          ;;
    "")            ;;
    *)             _fatal "Unknown flag: ${1}" ;;
esac

_check_monero

[[ -f "$WALLET_FILE" && -f "$WALLET_FILE.keys" ]] || decrypt

run_monero "$MODE"

encrypt

trap - EXIT INT TERM
rm -f "$WALLET_FILE" "$WALLET_FILE.keys"

