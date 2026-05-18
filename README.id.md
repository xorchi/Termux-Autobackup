# Termux-Autobackup

> 🇬🇧 [Read in English](README.md)

Repositori utilitas pribadi untuk Termux — kumpulan skrip dan alat untuk backup, manajemen sistem, manajemen kredensial WiFi, pengelolaan wallet Monero, dan berbagai utilitas kecil lainnya.

---

## Instalasi

```bash
pkg install git
git clone https://github.com/xorchi/Termux-Autobackup
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
│   ├── local-cloud.sh    # FileBrowser di jaringan lokal (tanpa Cloudflare)
│   ├── install-debian.sh # Setup otomatis proot-distro Debian dengan zsh + zinit
│   ├── enc.sh            # Enkripsi file dengan GPG
│   ├── dec.sh            # Dekripsi file GPG
│   ├── git-remote.sh     # Konfigurasi identitas git otomatis berdasarkan SSH remote
│   ├── wa-gojek.sh       # Generator pesan konfirmasi GoSend via WhatsApp
│   ├── webserver.sh      # Launcher web server lokal untuk subdirektori host/
│   ├── xmr-nodes.sh      # Ambil daftar node Monero yang tersedia
│   ├── fng.sh            # Indeks Fear & Greed kripto
│   ├── random.sh         # Generator angka acak (format lotere)
│   ├── repo-list.sh      # Daftar repo GitHub berdasarkan jumlah bintang
│   ├── main-repo.sh      # Reset repositori paket Termux ke resmi
│   ├── bip39             # Generator seed phrase BIP39 (biner)
│   ├── bip39cli.py       # Alat mnemonic BIP39/Monero — generate, validasi, derivasi alamat (BTC/ETH/BNB/SOL/XMR), konversi BIP39 ke seed Monero
│   ├── polyseed.py       # Konverter Polyseed 16 kata ke seed Monero 25 kata dengan dukungan passphrase
│   ├── generate_segwit_address.py  # Generator alamat SegWit BIP84 dari zpub
│   ├── btc-cycle.py      # Proyeksi siklus halving Bitcoin — estimasi bottom/ATH dengan weighted log regression
│   ├── btc_data.json     # Data historis siklus BTC (top dan bottom) untuk btc-cycle.py
│   ├── ema.py            # Screener EMA 200 daily untuk 100 koin teratas via Binance API
│   ├── xmr_supply_calculator.py  # Kalkulator supply XMR beredar secara deterministik
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
└── host/                 # Direktori self-hosting — isinya dikecualikan dari git
    └── index.html        # Halaman yang dihosting (via Tor hidden service / I2P eepsite)
```

---

## Kebutuhan

Install paket-paket berikut sebelum menggunakan script yang membutuhkannya:

```bash
pkg install git gpg python tor i2pd monero
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
CLOUD_PORT=""          # Port untuk FileBrowser cloud server (default: 8080)
CLOUD_STORAGE=""       # Direktori yang diekspos via cloud server (default: /sdcard)
LOCAL_PORT=""          # Port untuk FileBrowser server lokal
LOCAL_STORAGE=""       # Direktori yang diekspos via server lokal
LOCAL_GATEWAY=""       # IP gateway lokal (mis. 192.168.1.1) untuk deteksi IP
GITHUB_USERNAME=""     # Username GitHub Anda
PROFILE1_HOST=""       # SSH host untuk profil git 1 (mis. github.com)
PROFILE1_NAME=""       # Git user.name untuk profil 1
PROFILE1_EMAIL=""      # Git user.email untuk profil 1
PROFILE1_GPG=""        # Kunci GPG signing untuk profil 1
# Profil tambahan: PROFILE2_*, PROFILE3_*, dst.
```

---

## Wallet Monero (`xmr/main.sh`)

Wrapper Monero CLI yang diperkeras dengan enkripsi GPG saat tidak digunakan.

**Fitur:**
- File wallet dienkripsi GPG saat tidak aktif digunakan
- Mendukung mode Tor, clearnet, I2P, dan offline
- Pembersihan otomatis saat keluar secara tidak normal (SIGINT, SIGTERM)
- Mendeteksi dan membersihkan file plaintext sisa dari sesi sebelumnya yang crash
- Berbasis config (tidak ada nama wallet atau alamat node yang hardcoded)

**Kebutuhan:** `monero-wallet-cli`, `gpg`, `tor` (hanya untuk mode Tor), `i2pd` (hanya untuk mode I2P)

Direktori `vault/` disimpan permanen di `$PREFIX/var/vault/` dan hanya disalin ke `xmr/vault/` saat runtime berlangsung.

Buat file ini secara manual sebelum pertama kali menjalankan script.

**Config** (`$PREFIX/var/vault/config`):
```bash
WALLET_NAME="nama_wallet_kamu"
GPG_RECIPIENT="FINGERPRINT_KUNCI_GPG_KAMU"
NODE_CLEARNET="host:port"
NODE_ONION="host.onion:port"
NODE_I2P="host.b32.i2p:port"
```

**Penggunaan:**
```bash
xmr        # Default: Tor
xmr -c     # Clearnet
xmr -i     # I2P
xmr -o     # Offline
xmr -h     # Bantuan
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

Mengekspos direktori melalui FileBrowser lewat tunnel Cloudflare. Menampilkan QR code di terminal saat server siap. Membutuhkan `CLOUD_PORT` dan `CLOUD_STORAGE` di `others/config`.

```bash
bash utils/cloud-server.sh
```

**Kebutuhan:** `filebrowser`, `cloudflared`, `python3`, `qrcode`

Untuk akses di jaringan lokal tanpa Cloudflare, gunakan `local-cloud.sh`. Membutuhkan `LOCAL_PORT`, `LOCAL_STORAGE`, dan `LOCAL_GATEWAY` di `others/config`.

```bash
bash utils/local-cloud.sh
```

---

## WiFi Manager

Manajer kredensial WiFi berbasis SQLite dengan fitur generate QR code untuk berbagi dengan mudah.

```bash
cd wifi && python3 wifi_manager.py
```

---

## Utilitas Kripto

**Alat mnemonic BIP39/Monero** — tool interaktif dan CLI. Generate seed BIP39 atau Monero 25 kata, validasi, derivasi alamat (BTC semua tipe, ETH, BNB, SOL, XMR), konversi BIP39 ke seed Monero, terapkan offset passphrase native Monero. Zero dependency, stdlib saja.
```bash
python3 utils/bip39cli.py                          # interaktif
python3 utils/bip39cli.py generate 24
python3 utils/bip39cli.py generate --xmr
python3 utils/bip39cli.py derive "<mnemonic>" "" --coin btc
python3 utils/bip39cli.py --help
```

**Konverter Polyseed** — mengkonversi mnemonic Polyseed 16 kata (dengan passphrase opsional) ke seed Monero 25 kata dan primary address. Dilengkapi self-test terhadap test vector yang diketahui. Zero dependency, stdlib saja.
```bash
python3 utils/polyseed.py
```

**Generator alamat SegWit** — menurunkan alamat BIP84 native SegWit dari zpub. Mendukung chain change/receive dan rentang indeks kustom.
```bash
python3 utils/generate_segwit_address.py <zpub> --count 10
```

**Proyeksi siklus Bitcoin** — memproyeksikan bottom dan ATH siklus BTC berikutnya menggunakan weighted log regression pada data siklus halving historis. Data tersimpan di `btc_data.json`, dapat diedit via menu interaktif. Zero dependency, stdlib saja.
```bash
python3 utils/btc-cycle.py
```

**Screener EMA 200 daily** — memindai 100 koin teratas berdasarkan volume di Binance dan menampilkan koin dengan harga closing di atas EMA 200, diurutkan berdasarkan kedekatan terhadap EMA.
```bash
python3 utils/ema.py
```

**Kalkulator supply XMR** — menghitung total XMR beredar secara deterministik dengan mensimulasikan setiap blok dari genesis menggunakan rumus emisi resmi Monero. Mengambil tinggi blok dari API publik; semua kalkulasi supply dilakukan secara lokal.
```bash
python3 utils/xmr_supply_calculator.py
python3 utils/xmr_supply_calculator.py --verbose
```

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

**Konfigurator git remote** — mendeteksi otomatis URL SSH remote repo saat ini dan menerapkan identitas git yang sesuai (nama, email, kunci GPG) dari `others/config`. Jika tidak ditemukan kecocokan, menampilkan menu pemilihan profil secara manual.
```bash
bash utils/git-remote.sh
```

**Alat WhatsApp GoSend** — menghasilkan pesan konfirmasi pickup atau dropoff untuk pengiriman GoSend dan membukanya langsung di WhatsApp. Nama driver dibaca dari `PROFILE2_NAME` di `others/config`.
```bash
bash utils/wa-gojek.sh
```

**Launcher web server** — menjalankan HTTP server lokal di port 8080 untuk subdirektori tertentu di dalam `host/`. Menampilkan daftar direktori yang tersedia jika dipanggil tanpa argumen.
```bash
bash utils/webserver.sh toko
bash utils/webserver.sh   # tampilkan daftar
```
**Installer Debian** — setup otomatis proot-distro Debian Trixie dengan zsh, zinit, plugin (autosuggestions, syntax-highlighting, fzf-tab), neovim, eza, dan tema osx2 kustom.
```bash
bash utils/install-debian.sh
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

## Self-Hosting (`host/`)

Direktori `host/` diperuntukkan bagi file yang dihosting via Tor hidden service atau I2P eepsite. Isinya dikecualikan dari git — direktori tetap terlihat di repositori namun file-filenya bersifat privat.

Konfigurasikan Tor dan i2pd agar mengarah ke server lokal (mis. `python3 -m http.server 8080`) yang melayani direktori ini.

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
- File sensitif (`xmr/vault/`, `*.gpg`, `*.db`, `others/config`, `host/*`) dikecualikan melalui `.gitignore`.
- Repositori ini ditujukan untuk penggunaan pribadi. Sesuaikan path dan konfigurasi dengan lingkungan Anda sebelum digunakan.

