#!/usr/bin/env bash
# fng_minimal.sh — realtime Fear & Greed Index, super simple

API="https://api.alternative.me/fng/"

# Check dependencies
command -v curl >/dev/null || { echo "curl gak ada."; exit 1; }
command -v jq >/dev/null || { echo "jq gak ada."; exit 1; }

# Fetch data
raw=$(curl -sS "${API}?format=json&limit=1") || { echo "Failed to fetch API"; exit 1; }

value=$(echo "$raw" | jq -r '.data[0].value')
cls=$(echo "$raw" | jq -r '.data[0].value_classification')

# Determine emoji & color
case "$cls" in
  "Extreme Fear"|"Fear") EMO="🔴"; COLOR="\033[31m" ;;
  "Neutral") EMO="🟡"; COLOR="\033[33m" ;;
  "Greed"|"Extreme Greed") EMO="🟢"; COLOR="\033[32m" ;;
  *) EMO="⚪"; COLOR="\033[0m" ;;
esac

echo -e "${COLOR}${cls} ${EMO} ${value}${RESET}"
