#!/data/data/com.termux/files/usr/bin/bash
# git-remote.sh — Auto-configure git identity per repo based on SSH remote
# Save to: ~/Termux-Autobackup/utils/git-remote.sh

CONFIG_FILE="$HOME/Termux-Autobackup/others/config"

# ─── Load config ─────────────────────────────────────────────────────────────
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "[ERROR] Config file not found: $CONFIG_FILE"
    exit 1
fi
source "$CONFIG_FILE"

# ─── Verify inside a git repo ────────────────────────────────────────────────
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "[ERROR] Not a git repository."
    exit 1
fi

# ─── Count profiles defined in config ────────────────────────────────────────
get_profile_count() {
    local count=0
    local i=1
    while true; do
        local host_var="PROFILE${i}_HOST"
        [[ -z "${!host_var}" ]] && break
        count=$i
        ((i++))
    done
    echo "$count"
}

# ─── Apply profile by index ───────────────────────────────────────────────────
apply_profile() {
    local i="$1"
    local name_var="PROFILE${i}_NAME"
    local email_var="PROFILE${i}_EMAIL"
    local gpg_var="PROFILE${i}_GPG"

    git config user.name "${!name_var}"
    git config user.email "${!email_var}"
    git config user.signingkey "${!gpg_var}"
    git config commit.gpgsign true
    git config tag.gpgsign true

    echo ""
    echo "✓ Profile applied:"
    echo "  Name       : ${!name_var}"
    echo "  Email      : ${!email_var}"
    echo "  GPG Key    : ${!gpg_var}"
    echo "  GPG Sign   : commit + tag"
}

# ─── Set remote URL ───────────────────────────────────────────────────────────
set_remote() {
    local url="$1"
    if git remote get-url origin > /dev/null 2>&1; then
        git remote set-url origin "$url"
        echo "✓ Remote updated: $url"
    else
        git remote add origin "$url"
        echo "✓ Remote added: $url"
    fi
}

# ─── Show full profile menu ───────────────────────────────────────────────────
show_menu() {
    local count
    count=$(get_profile_count)
    local i=1
    while [[ $i -le $count ]]; do
        local host_var="PROFILE${i}_HOST"
        local name_var="PROFILE${i}_NAME"
        echo "  $i) ${!host_var} (${!name_var})"
        ((i++))
    done
}

# ─── Select profile from full menu ────────────────────────────────────────────
select_profile() {
    local count
    count=$(get_profile_count)
    show_menu
    echo ""
    read -r -p "Choice [1-${count}]: " choice
    if [[ "$choice" =~ ^[0-9]+$ ]] && [[ "$choice" -ge 1 ]] && [[ "$choice" -le "$count" ]]; then
        apply_profile "$choice"
    else
        echo "[ERROR] Invalid choice."
        exit 1
    fi
}

# ─── Detect profile from URL ──────────────────────────────────────────────────
detect_and_apply() {
    local url="$1"
    local count
    count=$(get_profile_count)

    local matches=()
    local i=1
    while [[ $i -le $count ]]; do
        local host_var="PROFILE${i}_HOST"
        if echo "$url" | grep -q "${!host_var}"; then
            matches+=("$i")
        fi
        ((i++))
    done

    if [[ ${#matches[@]} -eq 0 ]]; then
        return 1
    fi

    if [[ ${#matches[@]} -eq 1 ]]; then
        local host_var="PROFILE${matches[0]}_HOST"
        echo "[INFO] Detected: ${!host_var}"
        apply_profile "${matches[0]}"
        return 0
    fi

    # Multiple matches — show filtered menu
    echo "[INFO] Multiple profiles match. Select one:"
    for idx in "${matches[@]}"; do
        local host_var="PROFILE${idx}_HOST"
        local name_var="PROFILE${idx}_NAME"
        echo "  $idx) ${!host_var} (${!name_var})"
    done
    echo ""
    read -r -p "Choice: " choice
    local valid=false
    for idx in "${matches[@]}"; do
        if [[ "$choice" == "$idx" ]]; then
            valid=true
            apply_profile "$choice"
            break
        fi
    done
    if [[ "$valid" == false ]]; then
        echo "[ERROR] Invalid choice."
        exit 1
    fi
    return 0
}

# ─── Main logic ───────────────────────────────────────────────────────────────
REMOTE_URL=$(git remote get-url origin 2>/dev/null)

if [[ -n "$REMOTE_URL" ]]; then
    echo "[INFO] Remote found: $REMOTE_URL"
    if ! detect_and_apply "$REMOTE_URL"; then
        echo "[WARN] Remote not recognized. Select profile manually:"
        select_profile
    fi
else
    echo "[INFO] No remote found. Enter SSH remote URL:"
    read -r -p "URL: " input_url
    if [[ -z "$input_url" ]]; then
        echo "[ERROR] URL cannot be empty."
        exit 1
    fi
    set_remote "$input_url"
    if ! detect_and_apply "$input_url"; then
        echo "[WARN] Remote not recognized. Select profile manually:"
        select_profile
    fi
fi

