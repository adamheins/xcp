# Add cut/copy/paste functionality to the shell, much the same way it works in
# other parts of the system.

PST_DIR=$HOME/.pst
PST_CURR_DIR=$PST_DIR/current
PST_OLD_DIR=$PST_DIR/old


# Create the pst directories if they don't exist.
_pst_mkdirs() {
  [ ! -d $PST_CURR_DIR ] && mkdir -p $PST_CURR_DIR
  [ ! -d $PST_OLD_DIR  ] && mkdir -p $PST_OLD_DIR
}


# Move current contents to backup directory.
_pst_backup() {
  if [[ $(command ls $PST_CURR_DIR | wc -l) != 0 ]]; then
    mv $PST_CURR_DIR/* $PST_OLD_DIR

    # Only keep 5 most recent items in the backup area.
    command ls -t $PST_OLD_DIR | tail -n +6 | while read file; do
      rm -r "$PST_OLD_DIR/$file"
    done
  fi
}


# Behaves the same as normal `cp', unless exactly one non-flag argument is
# passed. If that is the case, it copies the file or directory for later
# pasting.
cp() {
  # If only a single non-option argument was passed to cp, this special version
  # of cp is used.
  if [ -n $1 ] && [ -z $2 ]; then
    first_char=$(echo "$1" | cut -c1)
    if [ "$first_char" != "-" ]; then

      # If the argument is neither a file nor a directory, abort.
      if [ ! -f "$1" ] && [ ! -d "$1" ]; then
        echo "No such file or directory $1."
        return 1
      fi

      _pst_mkdirs
      _pst_backup

      # Copy the src to the dest in the pst directory.
      local src="$1"
      local dest=$PST_CURR_DIR/$(basename "$1")
      if [ -d "$1" ]; then
        cp -r "$src" "$dest"
      else
        cp "$src" "$dest"
      fi
      return
    fi
  fi

  # Otherwise, fallback to normal built-in cp.
  command cp "$@"
}


# Behaves the same as normal `mv', unless exactly one non-flag argument is
# passed. If that is the case, it cuts the file or directory for later
# pasting.
mv() {
  if [ -n $1 ] && [ -z $2 ]; then
    first_char=$(echo "$1" | cut -c1)
    if [ "$first_char" != "-" ]; then

      # If the argument is neither a file nor a directory, abort.
      if [ ! -f "$1" ] && [ ! -d "$1" ]; then
        echo "No such file or directory $1."
        return 1
      fi

      _pst_mkdirs
      _pst_backup

      # Move in the new item.
      mv "$1" $PST_CURR_DIR/$(basename "$1")
      return
    fi
  fi

  # Otherwise, fallback to normal built-in mv.
  command mv "$@"
}


# Paste an item from the clipboard into the cwd.
_pst_item() {
  # If all is well, there should be only one item in the clipboard at any
  # given time, but just in case, we take the newest file.
  local item=$(command ls -t $PST_CURR_DIR | head -n 1)

  if [ -z $1 ]; then
    # If an item with the same name already exists, ask for confirmation before
    # pasting over it. This is only done when a name is not explicitly given,
    # as it is assumed the user knows what they're doing in that case.
    if [ -f ./"$item" ] || [ -d ./"$item" ]; then
      read -q "?An item named $item already exists. Continue? [yN]" || return
      echo ""
    fi
    echo "$item"
    cp -r "$PST_CURR_DIR/$item" .
  else
    echo "$item -> $1"
    cp -r "$PST_CURR_DIR/$item" "$1"
  fi
}


# Paste the last files or directories that were cut or copied.
pst() {
  [ ! -d $PST_DIR ] && return

  # With no argument, paste whatever is stored in the "clipboard" to the cwd.
  if [ -z $1 ]; then
    _pst_item
  else
    case "$1" in
      "-l"|"--list") command ls -A $PST_CURR_DIR ;;
      "-h"|"--help")
        echo "usage: pst [-chl] [dest]"
        echo ""
        echo "arguments:"
        echo "  -c, --clean  Remove all files from \$PST_DIR."
        echo "  -h, --help   Print this help message."
        echo "  -l, --list   List files in the \$PST_DIR."
      ;;
      "-c"|"--clean")
        setopt localoptions rmstarsilent
        rm -rf $PST_CURR_DIR/*(N)
        rm -rf $PST_OLD_DIR/*(N)
      ;;
      *) _pst_item "$1" ;;
    esac
  fi
}
