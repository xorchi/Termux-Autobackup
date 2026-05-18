#!/data/data/com.termux/files/usr/bin/bash

HOST_DIR="$HOME/Termux-Autobackup/host"
PORT=8080

if [[ -z "$1" ]]; then
    echo "Usage: webserver <name>"
    echo ""
    echo "Available:"
    for d in "$HOST_DIR"/*/; do
        [[ -d "$d" ]] && echo "  $(basename "$d")"
    done
    exit 1
fi

TARGET="$HOST_DIR/$1"

if [[ ! -d "$TARGET" ]]; then
    echo "[ERROR] Directory not found: $TARGET"
    exit 1
fi

echo "[INFO] Serving: $TARGET"
echo "[INFO] Port   : $PORT"
echo ""
cd "$TARGET" && python3 -m http.server "$PORT"
