import io
import os
import sys
import shutil
import tempfile
import time
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
    def setup_method(self):
        # mock an xcp directory
        self.config = xcp.XCPConfig()
        self.config.update({'root_dir': tempfile.mkdtemp()})
        self.clipboard = xcp.XCPClipboard(self.config)

        # mock a working directory
        self.cwd = tempfile.mkdtemp()
        os.chdir(self.cwd)

        # create some test files
        self.names = ['foo{}.txt'.format(i) for i in range(10)]
        self.texts = ['this is {}'.format(self.names[i]) for i in range(10)]

    def teardown_method(self):
        shutil.rmtree(self.config.root_dir)
        shutil.rmtree(self.cwd)

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
        with pytest.raises(FileNotFoundError):
            self.clipboard.copy('foo.txt')

    def test_backup(self):
        for name, text in zip(self.names, self.texts):
            path = self.write_cwd_file(name, text)

            # add a small delay so list_dir_by_age sorts properly
            time.sleep(0.01)
            self.clipboard.cut(path)

        # foo9   is in the current clipboard
        # foo4-8 are in backup
        # foo0-3 are gone
        paths = xcp.list_dir_by_age(self.config.back_dir)
        names = [os.path.basename(path) for path in paths]
        assert names == ['foo8.txt', 'foo7.txt', 'foo6.txt', 'foo5.txt',
                         'foo4.txt']

    def test_cut(self):
        path = self.write_cwd_file(self.names[0], self.texts[0])

        self.clipboard.cut(path)

        assert not os.path.exists(path)
        assert self.read_cb_current_file(self.names[0]) == self.texts[0]

    def test_peek(self):
        name = 'foo.txt'
        text = 'this is foo'
        path = self.write_cwd_file(name, text)

        self.clipboard.copy(path)
        assert self.clipboard.peek() == 'foo.txt'

    def test_paste(self):
        name = 'foo.txt'
        text = 'this is foo'
        path = self.write_cwd_file(name, text)

        self.clipboard.cut(path)
        self.clipboard.paste()

        assert self.read_cwd_file(name) == text

    def test_paste_and_rename(self):
        name = 'foo.txt'
        text = 'this is foo'
        path = self.write_cwd_file(name, text)

        self.clipboard.cut(path)
        self.clipboard.paste('bar.txt')

        assert self.read_cwd_file('bar.txt') == text

    def test_paste_empty_cb(self):
        with pytest.raises(FileNotFoundError):
            self.clipboard.paste()

    def test_paste_file_exists_y(self, monkeypatch):
        name = 'foo.txt'
        text = 'this is foo'
        path = self.write_cwd_file(name, text)

        # mock user confirming file overwrite
        monkeypatch.setattr('sys.stdin', io.StringIO('y'))

        self.clipboard.copy(path)
        self.clipboard.paste()

        assert self.read_cwd_file(name) == text

    def test_paste_file_exists_n(self, monkeypatch):
        name = 'foo.txt'
        text = 'this is foo'
        path = self.write_cwd_file(name, text)

        # mock user declining file overwrite
        monkeypatch.setattr('sys.stdin', io.StringIO('n'))

        self.clipboard.copy(path)

        with pytest.raises(Exception):
            self.clipboard.paste()

    def test_paste_dir_exists(self):
        # want to avoid overwriting an existing dir, but instead paste into it
        name = 'foo.txt'
        text = 'this is foo'
        dirname = 'bar'
        path = self.write_cwd_file(name, text)

        os.mkdir(dirname)

        self.clipboard.cut(path)
        self.clipboard.paste(dirname)

        dest = os.path.join(dirname, name)
        assert os.path.exists(dest)
        with open(dest) as f:
            assert f.read() == text
