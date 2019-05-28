#!/usr/bin/env python3

import colorama
import os
import shutil
import sys


HELP_TEXT = '''
usage: pst [-chl] [dest]

arguments:
-c, --clean  Remove all files from the clipboard, including backups.
-h, --help   Print this help message.
-l, --list   List files in the clipboard.
'''.strip()

PST_DIR = os.path.expanduser('~/.pst')
PST_CURR_DIR = os.path.join(PST_DIR, 'current')
PST_OLD_DIR = os.path.join(PST_DIR, 'old')

# Number of old items to keep in the backup directory.
NUM_OLD_ITEMS = 5


def yellow(s):
    ''' Color a string yellow. '''
    return colorama.Fore.YELLOW + s + colorama.Fore.RESET


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


def list_items():
    ''' List current item(s) in the clipboard. '''
    for item in os.listdir(PST_CURR_DIR):
        print(item)


def clean():
    ''' Remove all items, both current and backed up. '''
    shutil.rmtree(PST_CURR_DIR)
    shutil.rmtree(PST_OLD_DIR)
    make_dirs()


def cp(item):
    src = item
    name = os.path.basename(item)
    dest = os.path.join(PST_CURR_DIR, name)

    make_dirs()
    backup()

    copy_item(src, dest)


def mv(item):
    src = item
    name = os.path.basename(item)
    dest = os.path.join(PST_CURR_DIR, name)

    make_dirs()
    backup()

    shutil.move(src, dest)


def pst(dest=None):
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

    # Default to the pst command when nothing else fits.
    if len(args) == 0:
        pst()
    elif args[0] in ['cp', 'mv']:
        item = args[1]

        # Check that item to move or copy actually exists.
        if not os.path.exists(item):
            print('{} does not exist.'.format(yellow(item)))
            return 1

        if args[0] == 'cp':
            cp(item)
        else:
            mv(item)
    elif args[0] == 'pst':
        pst(args[1] if len(args) > 1 else None)
    elif args[0] in ['-l', '--list']:
        list_items()
    elif args[0] in ['-c', '--clean']:
        clean()
    elif args[0] in ['-h', '--help']:
        print(HELP_TEXT)
    else:
        pst(args[0])


if __name__ == '__main__':
    main()
