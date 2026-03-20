#!/usr/bin/env bash
# =============================================================
# install-debian.sh
# Instalasi & konfigurasi lengkap proot-distro Debian Trixie
# Jalankan dari Termux native
# =============================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RESET='\033[0m'

info()    { echo -e "${CYAN}[INFO]${RESET} $1"; }
success() { echo -e "${GREEN}[OK]${RESET} $1"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET} $1"; }
error()   { echo -e "${RED}[ERROR]${RESET} $1"; exit 1; }

DEBIAN_ROOT="/data/data/com.termux/files/usr/var/lib/proot-distro/installed-rootfs/debian/root"
TERMUX_THEMES="$HOME/.oh-my-zsh/custom/themes"

# =============================================================
# 1. Install proot-distro jika belum ada
# =============================================================
info "Memeriksa proot-distro..."

if ! command -v proot-distro &>/dev/null; then
  info "Menginstall proot-distro..."
  pkg install -y proot-distro
  success "proot-distro berhasil diinstall."
else
  success "proot-distro sudah tersedia."
fi

# =============================================================
# 2. Install Debian Trixie jika belum ada
# =============================================================
info "Memeriksa instalasi Debian..."

if [ ! -d "$DEBIAN_ROOT" ]; then
  info "Menginstall Debian Trixie..."
  proot-distro install debian
  success "Debian Trixie berhasil diinstall."
else
  warn "Debian sudah terinstall, lewati."
fi

# =============================================================
# 3. Salin tema osx2 ke dalam Debian
# =============================================================
info "Menyalin tema osx2..."

if [ -f "${TERMUX_THEMES}/osx2.zsh-theme" ]; then
  mkdir -p "${DEBIAN_ROOT}/.local/share/zinit"
  cp "${TERMUX_THEMES}/osx2.zsh-theme" \
    "${DEBIAN_ROOT}/.local/share/zinit/osx2.zsh-theme"
  success "Tema osx2 berhasil disalin."
else
  warn "Tema osx2 tidak ditemukan di ${TERMUX_THEMES}. Lewati langkah ini."
fi

# =============================================================
# 4. Tulis .zshrc ke dalam Debian
# =============================================================
info "Menulis konfigurasi .zshrc..."

cat > "${DEBIAN_ROOT}/.zshrc" << 'EOF'
### Zinit
if [[ ! -f $HOME/.local/share/zinit/zinit.git/zinit.zsh ]]; then
    command mkdir -p "$HOME/.local/share/zinit"
    command git clone https://github.com/zdharma-continuum/zinit "$HOME/.local/share/zinit/zinit.git"
fi

source "$HOME/.local/share/zinit/zinit.git/zinit.zsh"
autoload -Uz _zinit
(( ${+_comps} )) && _comps[zinit]=_zinit

### Plugins
zinit light zsh-users/zsh-autosuggestions
zinit light zsh-users/zsh-syntax-highlighting

### Tema osx2
autoload -U colors && colors
colors
function git_prompt_info() {
  local branch=$(git symbolic-ref --short HEAD 2>/dev/null)
  [[ -n "$branch" ]] && echo " ($branch)"
}
zinit snippet OMZ::lib/theme-and-appearance.zsh
zinit snippet ~/.local/share/zinit/osx2.zsh-theme

### fzf-tab
zinit light Aloxaf/fzf-tab

### Completion
autoload -Uz compinit && compinit
zstyle ':completion:*' menu select
setopt AUTO_CD

### Aliases
alias lt="eza --icons --tree"
alias lta="eza --icons --tree -lgha"
alias la="eza -a --icons=always"
alias ls="eza --icons=always"
alias t='eza -T --icons'
alias ta='eza -T -a --icons'
alias l='eza -l --icons'
alias ll='eza -lgha --icons'
alias c='clear'
alias ..='cd ..'
alias q='exit'
alias sd='cd /sdcard'
alias dl='cd /sdcard/Download'

### PATH — Debian lebih prioritas dari Termux
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH

### Syntax highlighting colors
ZSH_HIGHLIGHT_STYLES[command]='fg=cyan,bold'
ZSH_HIGHLIGHT_STYLES[builtin]='fg=cyan,bold'
ZSH_HIGHLIGHT_STYLES[alias]='fg=cyan,bold'
ZSH_HIGHLIGHT_STYLES[unknown-token]='fg=red,bold'
EOF

success ".zshrc berhasil ditulis."

# =============================================================
# 5. Tambahkan exec zsh ke .bashrc dalam Debian
# =============================================================
info "Mengatur default shell ke zsh..."

BASHRC="${DEBIAN_ROOT}/.bashrc"
grep -q 'exec zsh' "$BASHRC" 2>/dev/null || echo 'exec zsh' >> "$BASHRC"
success "exec zsh ditambahkan ke .bashrc."

# =============================================================
# 6. Jalankan setup paket di dalam Debian
# =============================================================
info "Menginstall paket-paket di dalam Debian..."

proot-distro login debian -- bash -c "
  apt update -y && apt install -y \
    zsh git curl fzf \
    fastfetch htop \
    gnupg gpg gpg-agent \
    openssh-client \
    neovim \
    python3 python3-pynvim \
    eza \
    sqv \
    xclip \
    locales \
    sudo \
    patch \
    openssl
"

success "Paket berhasil diinstall."

# =============================================================
# 7. Install Zinit di dalam Debian
# =============================================================
info "Menginstall Zinit di dalam Debian..."

proot-distro login debian -- bash -c "
  if [ ! -f \$HOME/.local/share/zinit/zinit.git/zinit.zsh ]; then
    mkdir -p \$HOME/.local/share/zinit
    git clone https://github.com/zdharma-continuum/zinit \
      \$HOME/.local/share/zinit/zinit.git
  fi
"

success "Zinit berhasil diinstall."

# =============================================================
# Selesai
# =============================================================
echo ""
echo -e "${GREEN}=====================================================${RESET}"
echo -e "${GREEN}  Instalasi selesai!${RESET}"
echo -e "${GREEN}  Masuk ke Debian dengan perintah: debian${RESET}"
echo -e "${GREEN}=====================================================${RESET}"
