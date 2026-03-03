# Termux-Autobackup

> 🇬🇧 [Read in English](README.md)

Repositori utilitas pribadi untuk Termux — kumpulan skrip dan alat untuk backup, manajemen sistem, manajemen kredensial WiFi, pengelolaan wallet Monero, dan berbagai utilitas kecil lainnya.

---

## Instalasi

```bash
pkg install git
git clone https://github.com/Rovikin/Termux-Autobackup
cd Termux-Autobackup
cp others/config.example others/config
# Edit others/config dan isi nilainya
```

---

## Struktur

```
Termux-Autobackup/
├── xmr/
│   ├── main.sh           # Manajer wallet Monero (terenkripsi GPG)
│   └── vault/            # Hanya saat runtime — dikecualikan dari git
│       └── config        # Konfigurasi wallet (nama, GPG recipient, node)
├── utils/
│   ├── backup.sh         # Backup penuh Termux ke /sdcard
│   ├── restore.sh        # Pulihkan Termux dari arsip backup
│   ├── cloud-server.sh   # Server FileBrowser + tunnel Cloudflare
│   ├── enc.sh            # Enkripsi file dengan GPG
│   ├── dec.sh            # Dekripsi file GPG
│   ├── xmr-nodes.sh      # Ambil daftar node Monero yang tersedia
│   ├── fng.sh            # Indeks Fear & Greed kripto
│   ├── random.sh         # Generator angka acak (format lotere)
│   ├── repo-list.sh      # Daftar repo GitHub berdasarkan jumlah bintang
│   ├── main-repo.sh      # Reset repositori paket Termux ke resmi
│   ├── bip39             # Generator seed phrase BIP39 (biner)
│   ├── pass.py           # Generator password aman
│   ├── username.py       # Generator username anonim
│   ├── gainer-loser.py   # Pelacak gainer/loser kripto teratas
│   ├── largest.py        # Temukan file terbesar di direktori Termux
│   ├── 100.py            # 100 kripto teratas berdasarkan market cap
│   └── exc.py            # Harga XMR/USD/IDR & konverter mata uang
├── wifi/
│   └── wifi_manager.py   # Manajer kredensial WiFi (SQLite)
├── others/
│   ├── config.example    # Template konfigurasi global
│   ├── dns.txt           # Daftar server DNS
│   └── gpg-pubkey.asc    # Kunci publik GPG untuk verifikasi commit
└── store/
    └── index.html        # Halaman toko lokal
```

---

## Kebutuhan

Install paket-paket berikut sebelum menggunakan script yang membutuhkannya:

```bash
pkg install git gpg python tor monero
pip install requests colorama pycoingecko --break-system-packages
```

Untuk cloud server:
```bash
pkg install cloudflared
pip install qrcode --break-system-packages
# filebrowser: install manual dari https://filebrowser.org
```

Untuk tools GitHub:
```bash
pkg install gh
```

---

## Konfigurasi

Salin template config dan isi nilainya sebelum pertama kali digunakan:

```bash
cp others/config.example others/config
```

`others/config` dikecualikan dari git. Isinya:

```bash
GPG_RECIPIENT=""       # Nama atau fingerprint kunci GPG Anda
CLOUD_PORT=""          # Port untuk FileBrowser (default: 8080)
CLOUD_STORAGE=""       # Direktori yang akan diekspos (default: /sdcard)
GITHUB_USERNAME=""     # Username GitHub Anda
```

---

## Wallet Monero (`xmr/main.sh`)

Wrapper Monero CLI yang diperkeras dengan enkripsi GPG saat tidak digunakan.

**Fitur:**
- File wallet dienkripsi GPG saat tidak aktif digunakan
- Mendukung mode Tor, clearnet, dan offline
- Pembersihan otomatis saat keluar secara tidak normal (SIGINT, SIGTERM)
- Mendeteksi dan membersihkan file plaintext sisa dari sesi sebelumnya yang crash
- Berbasis config (tidak ada nama wallet atau alamat node yang hardcoded)

**Kebutuhan:** `monero-wallet-cli`, `gpg`, `tor` (hanya untuk mode Tor)

Direktori `vault/` disimpan permanen di `$PREFIX/var/vault/` dan hanya disalin ke `xmr/vault/` saat runtime berlangsung.

Buat file ini secara manual sebelum pertama kali menjalankan script.

**Config** (`$PREFIX/var/vault/config`):
```bash
WALLET_NAME="nama_wallet_kamu"
GPG_RECIPIENT="FINGERPRINT_KUNCI_GPG_KAMU"
NODE_CLEARNET="host:port"
NODE_ONION="host.onion:port"
```

**Penggunaan:**
```bash
bash xmr/main.sh
# Kemudian pilih:
# 1 = Tor
# 2 = Clearnet
# 3 = Offline
```

---

## Backup & Restore

Backup dan restore lingkungan Termux secara penuh ke/dari `/sdcard`.

```bash
# Backup penuh
bash utils/backup.sh

# Pulihkan dari arsip backup
bash utils/restore.sh /sdcard/termux_backup_YYYYMMDD_HHMM.tar.gz
```

---

## Cloud Server

Mengekspos `/sdcard` melalui FileBrowser lewat tunnel Cloudflare. Menampilkan QR code di terminal saat server siap. Membutuhkan `CLOUD_PORT` dan `CLOUD_STORAGE` di `others/config`.

```bash
bash utils/cloud-server.sh
```

**Kebutuhan:** `filebrowser`, `cloudflared`, `python3`, `qrcode`

---

## WiFi Manager

Manajer kredensial WiFi berbasis SQLite dengan fitur generate QR code untuk berbagi dengan mudah.

```bash
cd wifi && python3 wifi_manager.py
```

---

## Utilitas Kripto

**Pelacak gainer/loser teratas** — menampilkan 10 gainer dan loser teratas dari 250 koin teratas berdasarkan market cap, dengan perubahan 1h/24h/7d/30d. Menyaring koin di bawah market cap $10M.
```bash
python3 utils/gainer-loser.py
```

**100 teratas berdasarkan market cap** — menampilkan 100 koin teratas dengan harga dan perubahan 30d.
```bash
python3 utils/100.py
```

**Harga XMR & konverter** — mengambil harga XMR terkini dalam USD dan IDR, dengan menu konversi mata uang interaktif (XMR/USD/IDR).
```bash
python3 utils/exc.py
```

**Indeks Fear & Greed** — mengambil indeks Fear & Greed kripto terkini dari alternative.me.
```bash
bash utils/fng.sh
```

**Daftar node Monero** — mengambil daftar node Monero aktif dari monero.fail.
```bash
bash utils/xmr-nodes.sh
```

---

## Utilitas Sistem

**Enkripsi/dekripsi GPG** — enkripsi atau dekripsi file menggunakan GPG recipient yang diset di `others/config`.
```bash
bash utils/enc.sh
bash utils/dec.sh
```

**Generator password** — menghasilkan password yang aman secara kriptografis menggunakan seluruh set karakter printable.
```bash
python3 utils/pass.py          # default 44 karakter
python3 utils/pass.py -l 128   # panjang kustom
```

**Generator username** — menghasilkan username anonim acak dari wordlist BIP39.
```bash
python3 utils/username.py
```

**Generator seed phrase BIP39** — menghasilkan mnemonic seed phrase yang kompatibel dengan BIP39.
```bash
./utils/bip39
```

**Temukan file terbesar** — memindai direktori Termux dan menampilkan 10 file terbesar.
```bash
python3 utils/largest.py
```

**Generator angka acak** — menghasilkan angka acak dalam format lotere (2D hingga 6D).
```bash
bash utils/random.sh
```

**Daftar repo GitHub** — menampilkan daftar repo GitHub Anda diurutkan berdasarkan jumlah bintang. Membutuhkan `GITHUB_USERNAME` di `others/config` dan `gh` CLI yang sudah terautentikasi.
```bash
bash utils/repo-list.sh
```

**Reset repositori Termux** — mereset `sources.list` ke repositori paket Termux resmi.
```bash
bash utils/main-repo.sh
```

---

## Kunci Publik GPG

File `others/gpg-pubkey.asc` berisi kunci publik GPG yang digunakan untuk menandatangani semua commit di repositori ini. Anda dapat mengimpornya untuk memverifikasi tanda tangan commit:

```bash
gpg --import others/gpg-pubkey.asc
git log --show-signature
```

---

## Catatan

- Semua commit ditandatangani dengan GPG.
- File sensitif (`xmr/vault/`, `*.gpg`, `*.db`, `others/config`) dikecualikan melalui `.gitignore`.
- Repositori ini ditujukan untuk penggunaan pribadi. Sesuaikan path dan konfigurasi dengan lingkungan Anda sebelum digunakan.
