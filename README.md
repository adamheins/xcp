# xcp
A simple shell script that provides commands to cut, copy, and paste files from
the command line. The motivation and basic usage is explained in [this blog
post](https://adamheins.com/blog/cut-copy-paste-files-cli).

I had previously implemented similar functionality as a much more complicated
Python tool, which you can see in earlier commits of this repo.

## Setup

Arrange for `xcp.sh` to be sourced by your shell, and run
```bash
mkdir ~/.xcp
```
once before using it.

## Usage

```bash
xmark <files>  # add some files to the clipboard
xcp <dest>     # copy clipboard files somewhere
xmv <dest>     # move clipboard files somewhere
```

Note that the clipboard files can be copied to as many destinations as desired,
but they can only be moved once.

## License

MIT
