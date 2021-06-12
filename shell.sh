

XCP_DIR=~/.xcp
CLIPBOARD_FILE=$XCP_DIR/clipboard


xcp() {
  echo "copy" > "$XCP_DIR"/clipboard
  realpath "$@" >> "$XCP_DIR"/clipboard
}

xmv() {
  echo "cut" > "$CLIPBOARD_FILE"
  realpath "$@" >> "$CLIPBOARD_FILE"
}

# paste files from clipboard
# executes [mv|cp] $files $args
# in other words, the files in the clipboard are passed as the first arguments
# to cp or mv, followed by all arguments passed to pst unaltered
pst() {
  local cmd files

  # build array of the files to by cut or copied
  tail -n +2 "$CLIPBOARD_FILE" | while read line; do
    files+=("$line")
  done

  # try to cut or copy files
  cmd=$(head -n 1 "$CLIPBOARD_FILE")
  if [ "$cmd" = "copy" ]; then
    cp $files $@
  elif [ "$cmd" = "cut" ]; then
    mv $files $@
  fi
}
