#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$SCRIPT_DIR/../others/config"

if [[ ! -f "$CONFIG" ]]; then
    echo "[ERROR] Config not found: $CONFIG" >&2
    echo "Salin others/config.example ke others/config lalu isi nilainya." >&2
    exit 1
fi

source "$CONFIG"

if [[ -z "${GPG_RECIPIENT:-}" ]]; then
    echo "[ERROR] GPG_RECIPIENT belum diisi di others/config." >&2
    exit 1
fi

echo "=== GPG Encrypt ==="
read -rp "Enter path to file to encrypt: " file_path

if [[ ! -f "$file_path" ]]; then
    echo "File not found." >&2
    exit 1
fi

output_file="${file_path}.gpg"
gpg --output "$output_file" --encrypt --recipient "$GPG_RECIPIENT" "$file_path"

if [[ $? -eq 0 ]]; then
    echo "File successfully encrypted to $output_file"
else
    echo "Failed to encrypt file." >&2
    exit 1
fi
