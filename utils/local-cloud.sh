#!/data/data/com.termux/files/usr/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$SCRIPT_DIR/../others/config"

if [[ ! -f "$CONFIG" ]]; then
    echo "[ERROR] Config not found: $CONFIG" >&2
    echo "Salin others/config.example ke others/config lalu isi nilainya." >&2
    exit 1
fi

source "$CONFIG"

if [[ -z "${LOCAL_PORT:-}" || -z "${LOCAL_STORAGE:-}" ]]; then
    echo "[ERROR] LOCAL_PORT or LOCAL_STORAGE not set in others/config." >&2
    exit 1
fi

PORT="$LOCAL_PORT"
STORAGE="$LOCAL_STORAGE"

echo "--- STARTING LOCAL SERVER ---"

# 1. Kill existing processes to avoid conflicts
pkill filebrowser
sleep 1

# 2. Dapatkan IP lokal
LOCAL_IP=$(ip addr show | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | cut -d'/' -f1 | head -n 1)
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
