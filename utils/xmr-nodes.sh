#!/bin/bash

URL="https://monero.fail/nodes.json"

curl -s "$URL" | jq -r '
  if .nodes then
    # Fetch all available nodes (Cleartext + Onion)
    .nodes[] | select(.available == true) | .address | sub("^https?://"; "")
  elif .monero then
    # Fetch from cleartext AND onion list
    (.monero.clear[], .monero.onion[]) | sub("^https?://"; "")
  else
    # Find all strings containing .onion or starting with http
    .. | strings | select(contains(".onion") or startswith("http")) | sub("^https?://"; "")
  end
' | bat -l txt --plain
