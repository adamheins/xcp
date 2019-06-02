# Add cut/copy/paste functionality to the shell, much the same way it works in
# other parts of the system.

# Behaves the same as normal `cp', unless exactly one non-flag argument is
# passed. If that is the case, it copies the file or directory for later
# pasting.
cp() {
  # If only a single non-option argument was passed to cp, this special version
  # of cp is used.
  if [ -n $1 ] && [ -z $2 ]; then
    first_char=$(echo "$1" | cut -c1)
    if [ "$first_char" != "-" ]; then
      xcp copy "$1"
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
      xcp cut "$1"
      return
    fi
  fi

  # Otherwise, fallback to normal built-in mv.
  command mv "$@"
}


# Paste the last files or directories that were cut or copied.
pst() {
  xcp paste $@
}
