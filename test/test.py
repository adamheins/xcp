import os
import sys
import shutil
import tempfile
import pytest
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from xcp import xcp


class TestConfig:

    def setup_method(self):
        self.config = xcp.XCPConfig()

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
        with pytest.raises(TypeError):
            self.config.update({'quiet': 1})

    def test_update_max_entries_not_int(self):
        with pytest.raises(TypeError):
            self.config.update({'max_entries': 5.0})

    def test_update_max_entries_negative(self):
        with pytest.raises(ValueError):
            self.config.update({'max_entries': -1})

    def test_load(self):
        d = {
            'quiet': False,
            'max_entries': 1,
            'root_dir': '/foo/bar',
        }

        fd, path = tempfile.mkstemp()

        os.environ[xcp.CONFIG_FILE_ENV_VAR] = path

        with os.fdopen(fd, 'w') as f:
            yaml.dump(d, f)
        self.config.load()

        assert self.config.as_dict() == d

        os.remove(path)


class TestClipboard:
    def setup_class(self):
        # mock an xcp directory
        self.config = xcp.XCPConfig()
        self.config.update({'root_dir': tempfile.mkdtemp()})

        # mock a working directory
        self.cwd = tempfile.mkdtemp()

        # create some test files
        self.names = ['foo{}.txt'.format(i) for i in range(10)]
        self.texts = ['this is {}'.format(self.names[i]) for i in range(10)]

    def teardown_class(self):
        shutil.rmtree(self.config.root_dir)
        shutil.rmtree(self.cwd)

    def setup_method(self):
        self.clipboard = xcp.XCPClipboard(self.config)

    def write_cwd_file(self, name, text):
        path = os.path.join(self.cwd, name)
        with open(path, 'w') as f:
            f.write(text)
        return path

    def read_cwd_file(self, name):
        with open(os.path.join(self.cwd, name)) as f:
            return f.read()

    def read_cb_current_file(self, name):
        with open(os.path.join(self.config.curr_dir, name)) as f:
            return f.read()

    def read_cb_backup_file(self, name):
        with open(os.path.join(self.config.back_dir, name)) as f:
            return f.read()

    def test_copy(self):
        name = 'foo.txt'
        text = 'this is foo'
        path = self.write_cwd_file(name, text)

        self.clipboard.copy(path)

        assert self.read_cwd_file(name) == text
        assert self.read_cb_current_file(name) == text

    def test_copy_no_exist(self):
        pass

    def test_backup(self):
        pass

    def test_backup_limit(self):
        pass

    def test_cut(self):
        path = self.write_cwd_file(self.names[0], self.texts[0])

        self.clipboard.cut(path)

        assert not os.path.exists(path)
        assert self.read_cb_current_file(self.names[0]) == self.texts[0]

    def test_peek(self, capsys):
        name = 'foo.txt'
        text = 'this is foo'
        path = self.write_cwd_file(name, text)

        self.clipboard.copy(path)
        self.clipboard.peek()

        captured = capsys.readouterr()
        assert captured.out == 'foo.txt\n'

    def test_paste(self):
        pass
