#!/data/data/com.termux/files/usr/bin/bash

# Get backup file path from argument
BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Cara pake: bash restore_termux.sh /sdcard/nama_file_backup.tar.gz"
    exit 1
fi

# Check if file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: File $BACKUP_FILE gak ketemu!"
    exit 1
fi

echo "--- WARNING! ---"
echo "Current Termux data (usr & home) will be deleted and replaced with the backup."
read -p "Are you sure you want to continue? (y/n): " CONFIRM

if [[ $CONFIRM == "y" || $CONFIRM == "Y" ]]; then
    echo "Menghapus data lama..."
    rm -rf /data/data/com.termux/files/usr /data/data/com.termux/files/home
    
    echo "Mengekstrak data backup..."
    tar -xzf "$BACKUP_FILE" -C /data/data/com.termux/
    
    if [ $? -eq 0 ]; then
        echo "--------------------------------------"
        echo "Restore successful!"
        echo "Please close Termux and reopen it."
        echo "--------------------------------------"
    else
        echo "Restore failed. Check the integrity of your tar file."
    fi
else
    echo "Restore dibatalkan."
fi
