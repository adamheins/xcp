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
  p|paste [name]  Copy the file currently in the clipboard to the current
                    working directory. Optionally rename the file.
  peek              Print the name of the file in the clipboard.
  clean             Clear the clipboard.
'''.strip()


CONFIG_FILE_PATH = os.path.expanduser('~/.config/xcp/config.yaml')
CONFIG_FILE_ENV_VAR = 'XCP_CONFIG_PATH'


def yellow(s):
    ''' Color a string yellow. '''
    # TODO check for tty
    return colorama.Fore.YELLOW + s + colorama.Fore.RESET


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


class XCPConfig(object):
    def __init__(self):
        self.quiet = True
        self.max_entries = 5
        self._set_root_dir(os.path.expanduser('~/.xcp'))

    def _set_root_dir(self, path):
        # Changing the root dir also requires changing the paths to subdirs, so
        # it gets its own method
        self.root_dir = path
        self.curr_dir = os.path.join(path, 'current')
        self.back_dir = os.path.join(path, 'old')

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

    def as_dict(self):
        ''' Dump entries as a dict. '''
        return {
            'quiet': self.quiet,
            'max_entries': self.max_entries,
            'root_dir': self.root_dir,
        }

    def load(self):
        ''' Load configuration from file. '''
        if CONFIG_FILE_ENV_VAR in os.environ:
            path = os.environ[CONFIG_FILE_ENV_VAR]
            with open(path) as f:
                self.update(yaml.load(f))
        else:
            if os.path.exists(CONFIG_FILE_PATH):
                self.update(yaml.load(CONFIG_FILE_PATH))
            else:
                with open(CONFIG_FILE_PATH) as f:
                    yaml.dump(self.as_dict(), f)


class XCPClipboard(object):
    def __init__(self, config):
        self.config = config

    def _make_dirs(self):
        ''' Make directory structure. '''
        for d in [self.config.root_dir, self.config.curr_dir,
                  self.config.back_dir]:
            if not os.path.isdir(d):
                os.mkdir(d)

    def _backup(self):
        ''' Back up files sitting in the paste buffer. '''
        # Move all files from current directory to the backup.
        for item in os.listdir(self.config.curr_dir):
            new_name = uniq_name(item, self.config.back_dir)
            shutil.move(os.path.join(self.config.curr_dir, item),
                        os.path.join(self.config.back_dir, new_name))

        # Remove all but the N most recent files in the backup directory.
        old_paths = list_dir_by_age(self.config.back_dir)
        for path in old_paths[self.config.max_entries:]:
            remove_item(path)

    def _insert(self, item):
        ''' Insert a new item into the clipboard.
            Returns: True if insert succesful, False otherwise. '''
        if not os.path.exists(item):
            raise FileNotFoundError('{} does not exist.'.format(yellow(item)))

        src = item
        name = os.path.basename(item)
        dest = os.path.join(self.config.curr_dir, name)

        self._make_dirs()
        self._backup()

        return src, dest

    def peek(self):
        ''' Get current file in the clipboard. '''
        return os.listdir(self.config.curr_dir)[0]

    def clean(self):
        ''' Remove all items, both current and backed up. '''
        shutil.rmtree(self.config.curr_dir)
        shutil.rmtree(self.config.back_dir)
        self._make_dirs()

    def copy(self, item):
        ''' Copy the item to the clipboard. '''
        src, dest = self._insert(item)
        copy_item(src, dest)

    def cut(self, item):
        ''' Move the item to the clipboard. '''
        src, dest = self._insert(item)
        shutil.move(src, dest)

    def paste(self, dest=None):
        ''' Paste item from the clipboard into the cwd, or optionally to
            `dest`. '''
        if not os.path.isdir(self.config.curr_dir):
            raise FileNotFoundError('Clipboard is empty.')

        paths = list_dir_by_age(self.config.curr_dir)
        if len(paths) == 0:
            raise FileNotFoundError('Clipboard is empty.')

        path = paths[0]
        item = os.path.basename(path)
        dest = dest if dest else item

        def check_exists(dest, count=0):
            ''' Handle when destination already exists. '''
            if count > 10:
                raise RuntimeError('Recursion too deep.')

            # If destination is a directory, nest.
            if os.path.isdir(dest):
                dest = os.path.join(dest, item)
                return check_exists(dest, count + 1)

            # If it's not a directory but still exists, ask before overwriting.
            if os.path.exists(dest):
                prompt = 'An item named {} already exists. Overwrite? [yN] '.format(yellow(dest))
                if not user_confirm(prompt):
                    raise Exception('Aborted by user.')
            return dest

        dest = check_exists(dest)

        copy_item(path, dest)
        if dest == item:
            return 'Pasted {}.'.format(yellow(item))
        else:
            return 'Pasted {} as {}.'.format(yellow(item), yellow(dest))


def main():
    args = sys.argv[1:]

    if len(args) == 0 or args[0] in ['-h', '--help', 'help']:
        print(HELP_TEXT)
        return 0

    cmd = args[0]
    item = args[1] if len(args) > 0 else None

    config = XCPConfig()
    config.load()
    clipboard = XCPClipboard(config)

    if cmd in ['c', 'copy']:
        if not item:
            print('File name required.')
            return 1
        clipboard.copy(item)
    elif cmd in ['x', 'cut']:
        if not item:
            print('File name required.')
            return 1
        clipboard.cut(item)
    elif cmd in ['v', 'p', 'paste']:
        print(clipboard.paste(item))
    elif cmd == 'peek':
        print(clipboard.peek())
    elif cmd == 'clean':
        clipboard.clean()
    else:
        print('Unrecognized command. Try --help.')
        return 1
    return 0


if __name__ == '__main__':
    main()
