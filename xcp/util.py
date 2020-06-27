import os
import shutil
import sys

import colorama


def yellow(s):
    ''' Color a string yellow. '''
    if sys.stdout.isatty():
        return colorama.Fore.YELLOW + s + colorama.Fore.RESET
    return s


def error_msg(s):
    return yellow('Error: ') + s


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
    return sorted(items, key=os.path.getctime, reverse=True)


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
