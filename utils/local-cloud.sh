#!/data/data/com.termux/files/usr/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$SCRIPT_DIR/../others/config"

if [[ ! -f "$CONFIG" ]]; then
    echo "[ERROR] Config not found: $CONFIG" >&2
    echo "Salin others/config.example ke others/config lalu isi nilainya." >&2
    exit 1
fi

source "$CONFIG"

if [[ -z "${LOCAL_PORT:-}" || -z "${LOCAL_STORAGE:-}" || -z "${LOCAL_GATEWAY:-}" ]]; then
    echo "[ERROR] LOCAL_PORT, LOCAL_STORAGE, or LOCAL_GATEWAY not set in others/config." >&2
    exit 1
fi

PORT="$LOCAL_PORT"
STORAGE="$LOCAL_STORAGE"
GATEWAY="$LOCAL_GATEWAY"

echo "--- STARTING LOCAL SERVER ---"

# 1. Kill existing processes to avoid conflicts
pkill filebrowser
sleep 1

# 2. Dapatkan IP lokal via Python (kompatibel Termux non-root)
LOCAL_IP=$(python3 -c "
import socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('$GATEWAY', 80))
    print(s.getsockname()[0])
    s.close()
except Exception:
    print('')
")

if [[ -z "$LOCAL_IP" ]]; then
    echo "[ERROR] Tidak dapat mendeteksi IP lokal. Periksa LOCAL_GATEWAY di config." >&2
    exit 1
fi

URL="http://$LOCAL_IP:$PORT"

# 3. Start FileBrowser
echo "[1/1] Menjalankan FileBrowser (lokal)..."
filebrowser -a 0.0.0.0 -p $PORT -r $STORAGE --baseurl / &

sleep 2

# 4. Tampilkan info dan QR Code
echo -e "\n\n===================================================="
echo -e "[INFO] LOCAL SERVER IS READY!"
echo -e "URL: $URL"
echo -e "====================================================\n"

python3 -c "import qrcode; qr = qrcode.QRCode(); qr.add_data('$URL'); qr.print_ascii()"

echo -e "\nScan the QR Code above to access from another device."
echo -e "====================================================\n"

# 5. Tetap berjalan di foreground agar tidak langsung exit
wait
