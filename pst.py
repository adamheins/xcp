#!/usr/bin/env python3

import colorama
import os
import shutil
import sys


PST_DIR = os.path.expanduser('~/.pst')
PST_CURR_DIR = os.path.join(PST_DIR, 'current')
PST_OLD_DIR = os.path.join(PST_DIR, 'old')

# Number of old items to keep in the backup directory.
NUM_OLD_ITEMS = 5


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
        os.rmdir(item)
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


def backup():
    # Move all files from current directory to the backup.
    for item in os.listdir(PST_CURR_DIR):
        new_name = uniq_name(item, PST_OLD_DIR)
        shutil.move(new_name, PST_OLD_DIR)

    # Remove all but the N most recent files in the backup directory.
    old_items = list_dir_by_age(PST_OLD_DIR)
    for item in old_items[NUM_OLD_ITEMS:]:
        remove_item(item)


def cp(item):
    src = item
    name = os.path.basename(item)
    # TODO not sure if I need to use absolute path
    dest = os.path.join(PST_CURR_DIR, name)
    print(src)
    print(dest)

    make_dirs()
    backup()

    copy_item(src, dest)


def mv(item):
    src = item
    name = os.path.basename(item)
    # TODO not sure if I need to use absolute path
    dest = os.path.join(PST_CURR_DIR, name)

    make_dirs()
    backup()

    shutil.move(src, dest)


def user_confirm(prompt):
    ans = raw_input(prompt)
    if len(ans) > 0:
        return ans[0] == 'y' or ans[0] == 'Y'
    return False


def pst(dest=None):
    if not os.path.isdir(PST_DIR):
        print('Nothing to paste.')
        return

    paths = list_dir_by_age(PST_CURR_DIR)
    if len(paths) == 0:
        print('Nothing to paste.')
        return

    path = paths[0]
    item = os.path.basebame(path)
    dest = dest if dest else item

    if os.path.exists(dest):
        if user_confirm('An item named {} already exists. Overwrite? [yN] '):
            copy_item(path, dest)
            if dest == item:
                print('Pasted {}.'.format(item))
            else:
                print('Pasted {} as {}.'.format(item, dest))


def main():
    args = sys.argv[1:]
    print(args)
    if args[0] == 'cp':
        cp(args[1])
    elif args[0] == 'mv':
        mv(args[1])
    elif args[0] == 'pst':
        pst(args[1] if len(args) > 1 else None)
    else:
        print('Unrecognized command {}.'.format(args[0]))
    # elif args[0] in ['-l', '--list']:
    #     pass
    # elif args[0] in ['-c', '--clean']:
    #     pass


if __name__ == '__main__':
    main()
