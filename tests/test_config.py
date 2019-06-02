import os
import tempfile

import pytest
import yaml

import xcp
from xcp import XCPConfig, XCPException


class TestConfig:
    def setup_method(self):
        self.config = XCPConfig()

    def test_default(self):
        assert self.config.as_dict() == {
            'quiet': True,
            'max_entries': 5,
            'root_dir': os.path.expanduser('~/.xcp'),
        }

    def test_update(self):
        d = {
            'quiet': False,
            'max_entries': 1,
            'root_dir': '/foo/bar',
        }
        self.config.update(d)
        assert self.config.as_dict() == d

    def test_update_quiet_not_bool(self):
        with pytest.raises(XCPException):
            self.config.update({'quiet': 1})

    def test_update_max_entries_not_int(self):
        with pytest.raises(XCPException):
            self.config.update({'max_entries': 5.0})

    def test_update_max_entries_negative(self):
        with pytest.raises(XCPException):
            self.config.update({'max_entries': -1})

    def test_load(self):
        d = {
            'quiet': False,
            'max_entries': 1,
            'root_dir': '/foo/bar',
        }

        fd, path = tempfile.mkstemp()

        os.environ[xcp.config.CONFIG_FILE_ENV_VAR] = path

        with os.fdopen(fd, 'w') as f:
            yaml.dump(d, f)
        self.config.load()

        assert self.config.as_dict() == d

        os.remove(path)
