#!/data/data/com.termux/files/usr/bin/bash

# Path config
DEST="/sdcard/termux_backup_$(date +%Y%m%d_%H%M).tar.gz"
SOURCE_DIR="/data/data/com.termux/"

echo "--- Memulai Backup Termux ---"

# Check storage access
if [ ! -d "/sdcard" ]; then
    echo "Error: Akses storage belom ada. Jalanin 'termux-setup-storage' dulu."
    exit 1
fi

# Start compression
echo "Processing... Please wait (do not close Termux!)"
tar -czf "$DEST" -C "$SOURCE_DIR" files

# Check if successful
if [ $? -eq 0 ]; then
    echo "--------------------------------------"
    echo "Done! Backup saved to: $DEST"
    echo "--------------------------------------"
else
    echo "Backup failed. Check your available storage."
    exit 1
fi
