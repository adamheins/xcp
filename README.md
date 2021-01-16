# xcp
A command line tool to cut, copy, and paste files.

## Installation
To get the `xcp` command, install using pip. __Only Python >=3.5 is supported.__
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

### Configuration
xcp allows the user to configure certain properties:
```
root_dir:    string   Directory to use for clipboard.
max_entries: int > 0  Number of most recent entries to keep backed up.
verbose:     bool     Set to true for verbose output.
```

These can be set in a yaml file at either `~/.config/xcp/config.yaml` or a file
path set by the environment variable `XCP_CONFIG_PATH` (the latter is given
priority, if the variable is set).

## Aliases
I actually like to make `cp` and `mv` perform xcp's copy and cut operations,
respectively, when only a single file is passed to them. I also create a
function `pst` to paste. A script `xcp.sh` located in the `sh` directory
provides this functionality when sourced. It should work with both bash and
zsh.

## Development
Testing is done using [pytest](https://docs.pytest.org/en/latest/). Simply run
`pytest .` in the `tests/` directory.

## License
MIT
