
XCP_DIR=~/.xcp
CLIPBOARD_FILE=$XCP_DIR/clipboard

# mark the file(s) for later use with cp or mv
xmark() {
  realpath "$@" > "$CLIPBOARD_FILE"
}


# copy the marked files
xcp() {
  local files
  while read line; do
    files+=("$line")
  done < "$CLIPBOARD_FILE"
  # flags:
  # -i  prompt before overwrite
  # -v  say what is being done
  cp -iv $files $@
}


# move the marked files
xmv() {
  local files
  while read line; do
    files+=("$line")
  done < "$CLIPBOARD_FILE"
  mv -iv $files $@
}
