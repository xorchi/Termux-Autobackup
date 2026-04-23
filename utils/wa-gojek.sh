#!/data/data/com.termux/files/usr/bin/bash
# wa-gojek.sh — GoSend WhatsApp confirmation message tool
# Save to: ~/Termux-Autobackup/utils/wa-gojek.sh

CONFIG_FILE="$HOME/Termux-Autobackup/others/config"

# ─── Load driver name from config ────────────────────────────────────────────
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "[ERROR] Config file not found: $CONFIG_FILE"
    exit 1
fi

DRIVER_NAME=$(grep "^PROFILE2_NAME=" "$CONFIG_FILE" | cut -d'=' -f2 | tr -d '"')

if [[ -z "$DRIVER_NAME" ]]; then
    echo "[ERROR] PROFILE2_NAME not found in config."
    exit 1
fi

# ─── Normalize Indonesian phone number ───────────────────────────────────────
normalize_phone() {
    local raw="$1"

    # Strip everything except digits
    local cleaned
    cleaned=$(echo "$raw" | tr -dc '0-9')

    # Convert to international format
    if [[ "$cleaned" =~ ^0 ]]; then
        cleaned="62${cleaned:1}"
    elif [[ "$cleaned" =~ ^62 ]]; then
        : # already correct
    elif [[ "$cleaned" =~ ^8 ]]; then
        cleaned="62${cleaned}"
    else
        echo ""
        return
    fi

    # Validate length: 62 + 8~12 digits
    local digits_after_62="${cleaned:2}"
    local len=${#digits_after_62}
    if [[ $len -lt 8 || $len -gt 12 ]]; then
        echo ""
        return
    fi

    echo "$cleaned"
}

# ─── URL encode message ───────────────────────────────────────────────────────
urlencode() {
    python3 -c "import urllib.parse, sys; print(urllib.parse.quote(sys.stdin.read(), safe=''))" <<< "$1"
}

# ─── Open WhatsApp ────────────────────────────────────────────────────────────
open_whatsapp() {
    local phone="$1"
    local message="$2"
    local encoded
    encoded=$(urlencode "$message")
    termux-open-url "whatsapp://send?phone=${phone}&text=${encoded}"
}

# ─── Input phone number ───────────────────────────────────────────────────────
input_phone() {
    local label="$1"
    local phone=""
    while true; do
        read -r -p "Phone number ($label): " raw
        phone=$(normalize_phone "$raw")
        if [[ -n "$phone" ]]; then
            echo "$phone"
            return
        else
            echo "[ERROR] Invalid phone number. Try again."
        fi
    done
}

# ─── Main menu ────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════╗"
echo "║     GoSend WA Confirmation   ║"
echo "╚══════════════════════════════╝"
echo ""
echo "  1) Pickup  — message to seller"
echo "  2) Dropoff — message to buyer"
echo ""
read -r -p "Select [1/2]: " mode

case "$mode" in
    1)
        echo ""
        read -r -p "Seller / store name : " seller_name
        read -r -p "Buyer / recipient name : " buyer_name
        phone=$(input_phone "seller")
        echo ""
        message="Halo, Kak *${seller_name^^}* $(printf '\xf0\x9f\x91\x8b')

Saya *${DRIVER_NAME^^}*, driver *GoSend* yang ditugaskan untuk Pickup dari:
Pengirim: *${seller_name^^}*

Untuk dikirimkan kepada:
Penerima: *${buyer_name^^}*.

Saat ini saya sudah tiba di lokasi pickup.

Terima kasih!
$(printf '\xf0\x9f\x99\x8f')"
        echo ""
        echo "─── Preview ───────────────────────"
        echo "$message"
        echo "───────────────────────────────────"
        echo ""
        read -r -p "Send? [y/n]: " confirm
        if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
            open_whatsapp "$phone" "$message"
            echo "Opening WhatsApp..."
        else
            echo "Cancelled."
        fi
        ;;
    2)
        echo ""
        read -r -p "Seller / store name : " seller_name
        read -r -p "Buyer / recipient name : " buyer_name
        phone=$(input_phone "buyer")
        echo ""
        message="Halo, Kak *${buyer_name^^}* $(printf '\xf0\x9f\x91\x8b')

Saya *${DRIVER_NAME^^}*, driver *GoSend* yang ditugaskan untuk mengantar paket dari:
Pengirim: *${seller_name^^}*

Untuk dikirimkan kepada:
Penerima: *${buyer_name^^}*.

Saat ini saya sudah tiba di alamat tujuan.

Terima kasih!
$(printf '\xf0\x9f\x99\x8f')"
        echo ""
        echo "─── Preview ───────────────────────"
        echo "$message"
        echo "───────────────────────────────────"
        echo ""
        read -r -p "Send? [y/n]: " confirm
        if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
            open_whatsapp "$phone" "$message"
            echo "Opening WhatsApp..."
        else
            echo "Cancelled."
        fi
        ;;
    *)
        echo "[ERROR] Invalid choice."
        exit 1
        ;;
esac
