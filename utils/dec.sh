#!/bin/bash

echo "=== GPG Decrypt ==="
read -rp "Enter path to .gpg file to decrypt: " file_path

if [[ ! -f "$file_path" ]]; then
    echo "File gak ketemu. Exit."
    exit 1
fi

# Strip .gpg extension and append .decrypted
output_file="${file_path%.gpg}.decrypted"

gpg --output "$output_file" --decrypt "$file_path"

if [[ $? -eq 0 ]]; then
    echo "File successfully decrypted to $output_file"
else
    echo "Failed to decrypt file."
fi
