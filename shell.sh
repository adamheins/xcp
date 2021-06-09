

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

pst() {
  local cmd dest files

  if [ -z "$1" ]; then
    dest="."
  else
    dest="$1"
  fi

  # build array of the files to by cut or copied
  tail -n +2 "$CLIPBOARD_FILE" | while read line; do
    files+=("$line")
  done

  # try to cut or copy files
  cmd=$(head -n 1 "$CLIPBOARD_FILE")
  if [ "$cmd" = "copy" ]; then
    cp -r $files "$dest" && echo "cp -r$files \"$dest\""
  elif [ "$cmd" = "cut" ]; then
    mv $files "$dest" && echo "mv$files \"$dest\""
  fi
}
