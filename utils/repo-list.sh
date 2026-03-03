#!/data/data/com.termux/files/usr/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$SCRIPT_DIR/../others/config"

if [[ ! -f "$CONFIG" ]]; then
    echo "[ERROR] Config not found: $CONFIG" >&2
    echo "Salin others/config.example ke others/config lalu isi nilainya." >&2
    exit 1
fi

source "$CONFIG"

if [[ -z "${GITHUB_USERNAME:-}" ]]; then
    echo "[ERROR] GITHUB_USERNAME belum diisi di others/config." >&2
    exit 1
fi

gh api users/"$GITHUB_USERNAME"/repos --paginate \
    --jq '.[] | "\(.stargazers_count) \(.name)"' | sort -nr | column -t
