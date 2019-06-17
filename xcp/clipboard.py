import os
import shutil

from xcp import util
from xcp.exception import XCPException


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
            new_name = util.uniq_name(item, self.config.back_dir)
            shutil.move(os.path.join(self.config.curr_dir, item),
                        os.path.join(self.config.back_dir, new_name))

        # Remove all but the N most recent files in the backup directory.
        old_paths = util.list_dir_by_age(self.config.back_dir)
        for path in old_paths[self.config.max_entries:]:
            util.remove_item(path)

    def _insert(self, item):
        ''' Insert a new item into the clipboard.
            Returns: True if insert succesful, False otherwise. '''
        if not os.path.exists(item):
            raise XCPException('{} does not exist.'.format(util.yellow(item)))

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
        util.copy_item(src, dest)

    def cut(self, item):
        ''' Move the item to the clipboard. '''
        src, dest = self._insert(item)
        shutil.move(src, dest)

    def paste(self, dest=None):
        ''' Paste item from the clipboard into the cwd, or optionally to
            `dest`. '''
        if not os.path.isdir(self.config.curr_dir):
            raise XCPException('Clipboard is empty.')

        paths = util.list_dir_by_age(self.config.curr_dir)
        if len(paths) == 0:
            raise XCPException('Clipboard is empty.')

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
                prompt = 'An item named {} already exists. Overwrite? [yN] '.format(util.yellow(dest))
                if not util.user_confirm(prompt):
                    raise Exception('Aborted by user.')
            return dest

        dest = check_exists(dest)

        util.copy_item(path, dest)
        if dest == item:
            return 'Pasted {}.'.format(util.yellow(item))
        else:
            return 'Pasted {} as {}.'.format(util.yellow(item),
                                             util.yellow(dest))
