#!/usr/bin/env bash
set -euo pipefail

VAULT_SRC="/data/data/com.termux/files/usr/var/vault"
WORKDIR="$HOME/Termux-Autobackup/xmr"

# ─── Trap ─────────────────────────────────────────────────────

_ENCRYPTED=0

_exit_guard() {
    if [[ $_ENCRYPTED -eq 0 ]]; then
        echo "[WARN] Script exited before encryption. Cleaning up..." >&2
        rm -f "$WORKDIR/$WALLET_NAME" "$WORKDIR/$WALLET_NAME.keys"
    fi
}

trap '_exit_guard' EXIT
trap 'exit 1' INT TERM

# ─── Load config ──────────────────────────────────────────────

if [[ ! -f "$VAULT_SRC/config" ]]; then
    echo "[FATAL] Config file not found at $VAULT_SRC/config." >&2
    exit 1
fi

# shellcheck source=/dev/null
source "$VAULT_SRC/config"

if [[ -z "${WALLET_NAME:-}" || -z "${GPG_RECIPIENT:-}" \
   || -z "${NODE_CLEARNET:-}" || -z "${NODE_ONION:-}" ]]; then
    echo "[FATAL] Config is invalid or incomplete." >&2
    exit 1
fi

WALLET_FILE="$WORKDIR/$WALLET_NAME"
MONERO_BIN=$(command -v monero-wallet-cli || true)

# ─── Leftover check ───────────────────────────────────────────

if [[ -f "$WORKDIR/$WALLET_NAME" || -f "$WORKDIR/$WALLET_NAME.keys" ]]; then
    echo "[WARN] Leftover from previous session found. Cleaning up..." >&2
    rm -f "$WORKDIR/$WALLET_NAME" "$WORKDIR/$WALLET_NAME.keys"
fi

# ─── Functions ────────────────────────────────────────────────

_check_monero() {
    if [[ -z "$MONERO_BIN" ]]; then
        echo "[WARN] monero-wallet-cli not found." >&2
        read -rp "Install now? (y/n) " yn
        if [[ "$yn" == "y" ]]; then
            pkg install monero -y
            MONERO_BIN=$(command -v monero-wallet-cli || true)
            if [[ -z "$MONERO_BIN" ]]; then
                echo "[FATAL] Installation failed." >&2
                exit 1
            fi
        else
            exit 1
        fi
    fi
}

decrypt() {
    local gpgdir="$HOME/.gnupg"

    mkdir -p "$WORKDIR"

    _decrypt_once() {
        gpg --yes -d -o "$WORKDIR/$WALLET_NAME"      "$VAULT_SRC/$WALLET_NAME.gpg"
        gpg --yes -d -o "$WORKDIR/$WALLET_NAME.keys" "$VAULT_SRC/$WALLET_NAME.keys.gpg"
    }

    _fix_gpg() {
        gpgconf --kill gpg-agent || true
        rm -f "$gpgdir"/*.lock "$gpgdir"/.#lock* 2>/dev/null || true
        chmod 700 "$gpgdir" 2>/dev/null || true
        gpgconf --launch gpg-agent || true
        sleep 0.5
    }

    local i=0
    until _decrypt_once; do
        i=$((i+1))
        echo "[WARN] Decrypt attempt $i failed." >&2
        if [[ $i -le 1 ]]; then
            _fix_gpg
            continue
        fi
        echo "[FATAL] Decrypt failed after retries." >&2
        exit 1
    done
}

encrypt() {
    local opts=(--batch --yes --trust-model always --encrypt --recipient "$GPG_RECIPIENT")
    gpg "${opts[@]}" -o "$VAULT_SRC/$WALLET_NAME.gpg"      "$WORKDIR/$WALLET_NAME"
    gpg "${opts[@]}" -o "$VAULT_SRC/$WALLET_NAME.keys.gpg" "$WORKDIR/$WALLET_NAME.keys"
}

run_monero() {
    local base_opts=(
        "--wallet-file" "$WALLET_FILE"
        "--log-file"    "/dev/null"
        "--log-level"   "0"
    )

    case "$1" in
        clearnet)
            "$MONERO_BIN" "${base_opts[@]}" \
                --daemon-address "$NODE_CLEARNET" \
                --trusted-daemon
            ;;
        offline)
            "$MONERO_BIN" "${base_opts[@]}" --offline
            ;;
        tor)
            _run_tor "${base_opts[@]}"
            ;;
    esac
}

_run_tor() {
    local base_opts=("$@")
    local tor_log="$HOME/.local/share/tor/log.txt"
    local timeout=30

    if ! command -v tor >/dev/null 2>&1; then
        echo "[FATAL] tor: not found." >&2
        exit 2
    fi

    pgrep -x tor >/dev/null 2>&1 || {
        mkdir -p "$(dirname "$tor_log")"
        tor > "$tor_log" 2>&1 &
    }

    local tor_opts=(
        "${base_opts[@]}"
        "--daemon-address" "$NODE_ONION"
        "--proxy"          "127.0.0.1:9050"
        "--trusted-daemon"
    )

    for _ in $(seq 1 "$timeout"); do
        if [[ -f "$tor_log" ]] && grep -q "Bootstrapped 100%" "$tor_log" 2>/dev/null; then
            "$MONERO_BIN" "${tor_opts[@]}"; return
        fi
        if (echo > /dev/tcp/127.0.0.1/9050) >/dev/null 2>&1 \
        || (echo > /dev/tcp/127.0.0.1/9150) >/dev/null 2>&1; then
            "$MONERO_BIN" "${tor_opts[@]}"; return
        fi
        if command -v nc >/dev/null 2>&1; then
            if nc -z 127.0.0.1 9050 >/dev/null 2>&1 \
            || nc -z 127.0.0.1 9150 >/dev/null 2>&1; then
                "$MONERO_BIN" "${tor_opts[@]}"; return
            fi
        fi
        sleep 1
    done

    echo "[ERROR] Tor timeout." >&2
    exit 1
}

# ─── Main ─────────────────────────────────────────────────────

_check_monero

if [[ ! -f "$WORKDIR/$WALLET_NAME" || ! -f "$WORKDIR/$WALLET_NAME.keys" ]]; then
    decrypt
fi

#read -rp "> " choice
choice=1
case "$choice" in
    1) run_monero tor      ;;
    2) run_monero clearnet ;;
    3) run_monero offline  ;;
    *) echo "[ERROR] Invalid choice." >&2; exit 1 ;;
esac

encrypt
echo "[+] Wallet encrypted."

_ENCRYPTED=1
trap - EXIT INT TERM

rm -f "$WORKDIR/$WALLET_NAME" "$WORKDIR/$WALLET_NAME.keys"
