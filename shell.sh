

XCP_DIR=~/.xcp
CLIPBOARD_FILE=$XCP_DIR/clipboard

# TODO, instead we could actually save the entire command...
# problem is we need to realpath the positional arguments
# we could also have a generic function first that "marks" the files, then xcp
# and xmv could be invoked after

xmark() {
  realpath "$@" > "$CLIPBOARD_FILE"
}


xcp() {
  local files
  while read line; do
    files+=("$line")
  done < "$CLIPBOARD_FILE"
  cp $files $@
}


xmv() {
  local files
  while read line; do
    files+=("$line")
  done < "$CLIPBOARD_FILE"
  mv $files $@
}


# xcp() {
#   echo "copy" > "$XCP_DIR"/clipboard
#   realpath "$@" >> "$XCP_DIR"/clipboard
# }
#
# xmv() {
#   echo "cut" > "$CLIPBOARD_FILE"
#   realpath "$@" >> "$CLIPBOARD_FILE"
# }
#
# # paste files from clipboard
# # executes [mv|cp] $files $args
# # in other words, the files in the clipboard are passed as the first arguments
# # to cp or mv, followed by all arguments passed to pst unaltered
# pst() {
#   local cmd files
#
#   # build array of the files to by cut or copied
#   tail -n +2 "$CLIPBOARD_FILE" | while read line; do
#     files+=("$line")
#   done
#
#   # try to cut or copy files
#   cmd=$(head -n 1 "$CLIPBOARD_FILE")
#   if [ "$cmd" = "copy" ]; then
#     cp $files $@
#   elif [ "$cmd" = "cut" ]; then
#     mv $files $@
#   fi
# }
