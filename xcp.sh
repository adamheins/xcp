
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
    # only add real files
    if [ -e "$line" ]; then
      files+=("$line")
    fi
  done < "$CLIPBOARD_FILE"

  if [ -z "$files" ]; then
    echo "no files in clipboard"
    return 1
  fi

  # flags:
  # -i  prompt before overwrite
  # -v  say what is being done
  cp -iv $files $@
}


# move the marked files
xmv() {
  local files
  while read line; do
    if [ -e "$line" ]; then
      files+=("$line")
    fi
  done < "$CLIPBOARD_FILE"

  if [ -z "$files" ]; then
    echo "no files in clipboard"
    return 1
  fi

  mv -iv $files $@

  # clear the clipboard now that files are moved
  echo > $CLIPBOARD_FILE
}
