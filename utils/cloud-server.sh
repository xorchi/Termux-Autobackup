#!/data/data/com.termux/files/usr/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$SCRIPT_DIR/../others/config"

if [[ ! -f "$CONFIG" ]]; then
    echo "[ERROR] Config not found: $CONFIG" >&2
    echo "Salin others/config.example ke others/config lalu isi nilainya." >&2
    exit 1
fi

source "$CONFIG"

if [[ -z "${CLOUD_PORT:-}" || -z "${CLOUD_STORAGE:-}" ]]; then
    echo "[ERROR] CLOUD_PORT or CLOUD_STORAGE not set in others/config." >&2
    exit 1
fi

PORT="$CLOUD_PORT"
STORAGE="$CLOUD_STORAGE"

echo "--- STARTING CLOUD SERVER ---"

# 1. Kill existing processes to avoid conflicts
pkill filebrowser
pkill cloudflared
sleep 1

# 2. Start FileBrowser in background
echo "[1/2] Menjalankan FileBrowser..."
filebrowser -a 127.0.0.1 -p $PORT -r $STORAGE > /dev/null 2>&1 &

# 3. QR Code notifier (background process)
(
    echo "Menunggu link Cloudflare siap..."
    
    LINK=""
    # Loop until Cloudflare tunnel URL is available
    while [ -z "$LINK" ]; do
        sleep 2
        LINK=$(curl -s http://127.0.0.1:20241/metrics | grep -o 'https://[^"]*\.trycloudflare\.com' | head -n 1)
    done

    # Brief delay to let Cloudflared finish printing logs
    sleep 2

    # Display QR Code in terminal
    echo -e "\n\n===================================================="
    echo -e "[INFO] CLOUD SERVER IS READY!"
    echo -e "URL: $LINK"
    echo -e "====================================================\n"
    
    # Generate QR code via Python one-liner
    python3 -c "import qrcode; qr = qrcode.QRCode(); qr.add_data('$LINK'); qr.print_ascii()"
    
    echo -e "\nScan the QR Code above to access from another device."
    echo -e "====================================================\n"
) &

# 4. Start Cloudflared
# Runs in foreground to maintain the tunnel connection
echo "[2/2] Membuka jalur internet via Cloudflare..."
echo "----------------------------------------------------"
cloudflared tunnel --url http://127.0.0.1:$PORT --metrics 127.0.0.1:20241
