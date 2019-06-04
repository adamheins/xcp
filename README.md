# xcp
Cut, copy, and paste files from the command line.

## Installation
```
pip install xcp-tool
```

## Usage
```
usage: xcp <command> <args>

commands:
  x|cut   <file>  Move the file into the clipboard. The file is removed from
                  its current location.
  c|copy  <file>  Copy the file into the clipboard. The file also remains in
                  its current location.
  p|paste [name]  Copy the file currently in the clipboard to the current
                  working directory. Optionally rename the file.
  peek            Print the name of the file in the clipboard.
  clean           Clear the clipboard.
  help            Print this message.
```

## Aliases
I actually like to make `cp` and `mv` perform xcp's copy and cut operations,
respectively, when only a single file is passed to them. I also create a
function `pst` to paste. A script `xcp.sh` located in the `sh` directory
provides this functionality when sourced. It should work with both bash and
zsh.

## License
MIT.
