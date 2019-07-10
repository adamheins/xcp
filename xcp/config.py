import os

import yaml

from xcp.exception import XCPException


CONFIG_FILE_PATH = os.path.expanduser('~/.config/xcp/config.yaml')
CONFIG_FILE_ENV_VAR = 'XCP_CONFIG_PATH'


class XCPConfig(object):
    def __init__(self):
        self.verbose = True
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
        if 'verbose' in d:
            v = d['verbose']
            if type(v) is not bool:
                raise XCPException('verbose parameter must be of type bool')
            else:
                self.verbose = v

        if 'max_entries' in d:
            v = d['max_entries']
            if type(v) is not int:
                raise XCPException('max_entries parameter must be of type int')
            if v < 0:
                raise XCPException('max_entries must be non-negative')
            self.max_entries = v

        if 'root_dir' in d:
            self._set_root_dir(d['root_dir'])

    def as_dict(self):
        ''' Dump entries as a dict. '''
        return {
            'verbose': self.verbose,
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
                os.makedirs(os.path.dirname(CONFIG_FILE_PATH), exist_ok=True)
                with open(CONFIG_FILE_PATH, 'w') as f:
                    yaml.dump(self.as_dict(), f)
