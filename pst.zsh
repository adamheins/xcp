# Add cut/copy/paste functionality to the shell, much the same way it works in
# other parts of the system.

# Get script's directory.
PST_SRC_DIR=${0:a:h}

# If the script is a symlink, we want to follow the symlink back to we can
# access the executable.
if [ -h $0 ]; then
  PST_SRC_DIR=$(dirname $(readlink $0))
fi

PST_PY=PST_SRC_DIR/pst.py


# Behaves the same as normal `cp', unless exactly one non-flag argument is
# passed. If that is the case, it copies the file or directory for later
# pasting.
cp() {
  # If only a single non-option argument was passed to cp, this special version
  # of cp is used.
  if [ -n $1 ] && [ -z $2 ]; then
    first_char=$(echo "$1" | cut -c1)
    if [ "$first_char" != "-" ]; then
      $PST_PY cp "$1"
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
      $PST_PY mv "$1"
      return
    fi
  fi

  # Otherwise, fallback to normal built-in mv.
  command mv "$@"
}


# Paste the last files or directories that were cut or copied.
pst() {
  [ ! -d $PST_DIR ] && return

  # With no argument, paste whatever is stored in the "clipboard" to the cwd.
  if [ -z $1 ]; then
    $PST_PY pst
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
      *) $PST_PY pst "$1" ;;
    esac
  fi
}
