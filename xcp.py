#!/usr/bin/env python3

import colorama
import os
import shutil
import sys
import yaml




HELP_TEXT = '''
usage: xcp <command> <args>

commands:
  x|cut  <file>     Move the file into the clipboard. The file is removed from
                    its current location.
  c|copy <file>     Copy the file into the clipboard. The file also remains in
                    its current location.
  v|p|paste [name]  Copy the file currently in the clipboard to the current
                    working directory. Optionally rename the file.
  peek              Print the name of the file in the clipboard.
  clean             Clear the clipboard.
'''.strip()


PST_DIR = os.path.expanduser('~/.pst')
PST_CURR_DIR = os.path.join(PST_DIR, 'current')
PST_OLD_DIR = os.path.join(PST_DIR, 'old')

# Number of old items to keep in the backup directory.
NUM_OLD_ITEMS = 5


CONFIG_FILE_PATH = os.path.expanduser('~/.config/xcp/config.yaml')


DEFAULT_CONFIG = {
    'quiet': False,
    'clip_dir': os.path.expanduser('~/.pst'),
    'clip_size': 5
}


# TODO need to think about how best to organize this
# seems like what I actually want is a customized dictionary
class XCPConfig(object):
    def __init__(self):
        self.quiet = True
        self.max_entries = 5
        self._set_root_dir(os.path.expanduser('~/.xcp'))

    def _set_root_dir(self, path):
        self.root_dir = path
        self.curr_dir = os.path.join(path, 'current')
        self.back_dir = os.path.join(path, 'old')

    def make_dirs(self):
        ''' Make directory structure. '''
        for d in [self.root_dir, self.curr_dir, self.back_dir]:
            if not os.path.isdir(d):
                os.mkdir(d)

    def update(self, d):
        '''  Update entries from a dict. '''
        if 'quiet' in d:
            v = d['quiet']
            if type(v) is not bool:
                raise TypeError('quiet parameter must be of type bool')
            else:
                self.quiet = v

        if 'max_entries' in d:
            v = d['max_entries']
            if type(v) is not int:
                raise TypeError('max_entries parameter must be of type int')
            if v < 0:
                raise ValueError('max_entries must be non-negative')
            self.max_entries = v

        if 'root_dir' in d:
            self._set_root_dir(d['root_dir'])

    def dump(self):
        ''' Dump entries as a dict. '''
        return {
            'quiet': self.quiet,
            'max_entries': self.max_entries,
            'root_dir': self.root_dir,
        }


def yellow(s):
    ''' Color a string yellow. '''
    return colorama.Fore.YELLOW + s + colorama.Fore.RESET


def load_config():
    if os.env('XCP_CONFIG_PATH'):
        config_path = os.env('XCP_CONF_PATH')
        config = yaml.load(config_path)
    else:
        if os.path.exists(CONFIG_FILE_PATH):
            config = yaml.load(CONFIG_FILE_PATH)
        else:
            # if the config file doesn't exist yet, create it and write the
            # default config params
            with open(CONFIG_FILE_PATH) as f:
                yaml.dump(DEFAULT_CONFIG, f)

    # merge loaded config with defaults to fill any missing fields
    config = {**DEFAULT_CONFIG, **config}

    return config


def make_dirs():
    ''' Create high-level pst directories if they don't already exist. '''
    for d in [PST_DIR, PST_CURR_DIR, PST_OLD_DIR]:
        if not os.path.isdir(d):
            os.mkdir(d)


def copy_item(src, dest):
    ''' Copy file or directory `src` to `dest`. '''
    if os.path.isdir(src):
        shutil.copytree(src, dest)
    else:
        shutil.copy(src, dest)


def remove_item(item):
    ''' Remove file or directory `item`. '''
    if os.path.isdir(item):
        shutil.rmtree(item)
    else:
        os.remove(item)


def list_dir_by_age(d):
    ''' Returns absolute paths of items in directory d, sorted by modification
        time, newest first. Emulates `ls -t`. '''
    items = [os.path.join(d, item) for item in os.listdir(d)]
    return sorted(items, key=os.path.getmtime, reverse=True)


def uniq_name(name, d):
    ''' Return a unique name based on `name` relative to the files in directory
        `d`. '''
    counter = 1
    new_name = name
    while os.path.exists(os.path.join(d, new_name)):
        new_name = '{}_{}'.format(name, counter)
        counter += 1
    return new_name


def user_confirm(prompt):
    ''' Prompt user for confirmation. '''
    ans = input(prompt)
    if len(ans) > 0:
        return ans[0] == 'y' or ans[0] == 'Y'
    return False


def backup():
    ''' Back up files sitting in the paste buffer. '''
    # Move all files from current directory to the backup.
    for item in os.listdir(PST_CURR_DIR):
        new_name = uniq_name(item, PST_OLD_DIR)
        shutil.move(os.path.join(PST_CURR_DIR, item),
                    os.path.join(PST_OLD_DIR, new_name))

    # Remove all but the N most recent files in the backup directory.
    old_paths = list_dir_by_age(PST_OLD_DIR)
    for path in old_paths[NUM_OLD_ITEMS:]:
        remove_item(path)


def peek_clip():
    ''' Get current file in the clipboard. '''
    print(os.listdir(PST_CURR_DIR)[0])


def clean_clip():
    ''' Remove all items, both current and backed up. '''
    shutil.rmtree(PST_CURR_DIR)
    shutil.rmtree(PST_OLD_DIR)
    make_dirs()


def copy_to_clip(item):
    ''' Copy the item to the clipboard. '''
    if not os.path.exists(item):
        print('{} does not exist.'.format(yellow(item)))
        return 1

    src = item
    name = os.path.basename(item)
    dest = os.path.join(PST_CURR_DIR, name)

    make_dirs()
    backup()

    copy_item(src, dest)


def move_to_clip(item):
    ''' Move the item to the clipboard. '''
    if not os.path.exists(item):
        print('{} does not exist.'.format(yellow(item)))
        return 1

    src = item
    name = os.path.basename(item)
    dest = os.path.join(PST_CURR_DIR, name)

    make_dirs()
    backup()

    shutil.move(src, dest)


def paste_from_clip(dest=None):
    if not os.path.isdir(PST_DIR):
        print('Nothing to paste.')
        return

    paths = list_dir_by_age(PST_CURR_DIR)
    if len(paths) == 0:
        print('Nothing to paste.')
        return

    # TODO should handle pasting into a directory without overwriting the
    # directory. Frankly, we can't overwrite a directory so we should warn
    # about this too.

    path = paths[0]
    item = os.path.basename(path)
    dest = dest if dest else item

    # If the destination already exists, we ask the user to confirm before
    # overwriting.
    if os.path.exists(dest):
        prompt = 'An item named {} already exists. Overwrite? [yN] '.format(yellow(dest))
        overwrite = user_confirm(prompt)
        if not overwrite:
            print('Aborted')
            return

    copy_item(path, dest)
    if dest == item:
        print('Pasted {}.'.format(yellow(item)))
    else:
        print('Pasted {} as {}.'.format(yellow(item), yellow(dest)))


def main():
    args = sys.argv[1:]

    if len(args) == 0 or args[0] in ['-h', '--help', 'help']:
        print(HELP_TEXT)
        return 0

    cmd = args[0]
    item = args[1] if len(args) > 0 else None

    if cmd in ['c', 'copy']:
        if not item:
            print('File name required.')
            return 1
        copy_to_clip(args[1])
    elif cmd in ['x', 'cut']:
        if not item:
            print('File name required.')
            return 1
        move_to_clip(args[1])
    elif cmd in ['p', 'paste']:
        paste_from_clip(item)
    elif cmd == 'peek':
        peek_clip()
    elif cmd == 'clean':
        clean_clip()
    else:
        print('Unrecognized command. Try --help.')
        return 1
    return 0

    # Default to the pst command when nothing else fits.
    # if len(args) == 0:
    #     pst()
    # elif args[0] in ['cp', 'mv']:
    #     item = args[1]
    #
    #     # Check that item to move or copy actually exists.
    #     if not os.path.exists(item):
    #         print('{} does not exist.'.format(yellow(item)))
    #         return 1
    #
    #     if args[0] == 'cp':
    #         cp(item)
    #     else:
    #         mv(item)
    # elif args[0] == 'pst':
    #     pst(args[1] if len(args) > 1 else None)
    # elif args[0] in ['-l', '--list']:
    #     list_items()
    # elif args[0] in ['-c', '--clean']:
    #     clean()
    # elif args[0] in ['-h', '--help']:
    #     print(HELP_TEXT)
    # else:
    #     pst(args[0])


if __name__ == '__main__':
    main()
