#!/usr/bin/env bash
# Detect duplicate/overlapping keymaps across global and mode profiles
set -euo pipefail

CONFIG_DIR=${XDG_CONFIG_HOME:-$HOME/.config}/kitty

scan_files=(
  "$CONFIG_DIR/includes/keymaps.conf"
  "$CONFIG_DIR/modes/demo.conf"
  "$CONFIG_DIR/modes/work.conf"
)

echo "Scanning keymaps..."

awk '
  BEGIN{print "file,key,command"}
  /^[[:space:]]*map[[:space:]]/ {
    file=FILENAME
    # strip leading spaces and comments
    line=$0
    sub(/^\s+/,"",line)
    if(line ~ /^#/){next}
    # capture key (2nd token) and the rest
    n=split(line, a, /[\t ]+/)
    if(n>=3){
      key=a[2]
      cmd=""
      for(i=3;i<=n;i++){cmd=cmd a[i] (i<n?" ":"")}
      gsub(/,/,";",cmd)
      print file "," key "," cmd
    }
  }
' "${scan_files[@]}" |
  awk -F, 'NR>1{print $2"|"$1"|"$3}' |
  sort |
  tee /tmp/kitty-keymaps.csv >/dev/null

echo
echo "Duplicates by key:"
cut -d'|' -f1 /tmp/kitty-keymaps.csv | sort | uniq -c | awk '$1>1{print $0}' || true

echo
echo "Detail for duplicates:"
awk -F'|' 'NR==FNR{if($1 in seen) dup[$1]=1; seen[$1]=1; next} {if($1 in dup){print $0}}' \
  <(cut -d'|' -f1 /tmp/kitty-keymaps.csv | sort | uniq -c | awk '$1>1{print $2}') \
  /tmp/kitty-keymaps.csv || true

echo
echo "Note: some duplicates are intentional across modes; check global vs mode conflicts."

