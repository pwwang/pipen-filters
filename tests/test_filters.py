import pytest
from collections import namedtuple
from pipen_filters.filters import FILTERS

f = namedtuple("f", FILTERS.keys())(*FILTERS.values())


# type: ignore [reportUndefinedVariable]
def test_realpath(tmp_path):
    target = tmp_path / "a"
    source = tmp_path / "b"
    source.write_text("")
    target.symlink_to(source)
    assert f.realpath(target) == str(source)


def test_slugify():
    assert f.slugify("a b") == "a-b"


def test_readlink(tmp_path):
    target = tmp_path / "a"
    source = tmp_path / "b"
    source.write_text("")
    target.symlink_to(source)
    assert f.readlink(target) == str(source)


def test_dirname():
    assert f.dirname("/a/b") == "/a"


def test_basename():
    assert f.basename("/a/b/c.txt") == "c.txt"


def test_commonprefix():
    assert f.commonprefix("/a/b/abc.txt", "/a/b/abc.png") == "abc."
    assert (
        f.commonprefix("/a/b/abc.txt", "/a/b/abc.png", basename_only=False)
        == "/a/b/abc."
    )


def test_ext():
    assert f.ext("/a/b.txt") == ".txt"
    assert f.ext("/a/b.txt.gz", ignore=".gz") == ".txt"
    assert f.ext("/a/b.txt.gz", ignore=[".gz"]) == ".txt"
    assert f.ext("/a/b.txt.gz", ignore=[".gz", "txt"], recursive=True) == ""
    assert f.ext("/a/b.x.txt.gz", ignore=[".gz", "txt"], recursive=True) == ".x"


def test_ext0():
    assert f.ext0("/a/b.txt") == "txt"
    assert f.ext0("/a/b.txt.gz", ignore=".gz") == "txt"
    assert f.ext0("/a/b.txt.gz", ignore=[".gz"]) == "txt"
    assert f.ext0("/a/b.txt.gz", ignore=[".gz", "txt"], recursive=True) == ""
    assert f.ext0("/a/b.x.txt.gz", ignore=[".gz", "txt"], recursive=True) == "x"


def test_prefix():
    assert f.prefix("/a/b.c.txt") == "/a/b.c"
    assert f.prefix("/a/b.c.txt", ignore=".txt") == "/a/b"
    assert f.prefix("/a/b.c.txt", ignore=[".txt"]) == "/a/b"
    assert f.prefix("/a/c.d.e.txt", ignore=[".txt", "e"], recursive=True) == "/a/c"
    assert f.prefix("/a/c.d.e.txt", ignore=[".txt", "e"], recursive=False) == "/a/c.d"


def test_prefix0():
    assert f.prefix0("/a/b.c.txt") == "/a/b"
    assert f.prefix0("/a/b.c.txt", ignore=".txt") == "/a/b"
    assert f.prefix0("/a/b.c.txt", ignore=[".txt"]) == "/a/b"
    assert f.prefix0("/a/b.c.txt", ignore=[".txt", "c"], recursive=True) == "/a/b"
    assert f.prefix0("/a/b.c.d.e.txt", ignore=[".txt", "c"], recursive=True) == "/a/b"


def test_filename():
    assert f.filename("/a/b.c.txt") == "b.c"
    assert f.filename("/a/b.c.txt", ignore=".txt") == "b"
    assert f.filename("/a/b.c.txt", ignore=[".txt"]) == "b"
    assert f.filename("/a/b.c.d.txt", ignore=[".txt", "d"], recursive=True) == "b"
    assert f.filename("/a/b.c.d.txt", ignore=[".txt", "d"], recursive=False) == "b.c"


def test_filename0():
    assert f.filename0("/a/b.c.txt") == "b"
    assert f.filename0("/a/b.c.txt", ignore=".txt") == "b"
    assert f.filename0("/a/b.c.txt", ignore=[".txt"]) == "b"
    assert f.filename0("/a/b.c.txt", ignore=[".txt", "c"], recursive=True) == "b"
    assert f.filename0("/a/b.c.d.e.txt", ignore=[".txt", "c"], recursive=True) == "b"


def test_quote():
    assert f.quote("1") == '"1"'


def test_squote():
    assert f.squote("1") == "'1'"


def test_joinpaths():
    assert f.joinpaths("a", "b") == "a/b"


def test_json():
    assert f.json({"a": 1}) == '{"a": 1}'
    assert f.json_dumps({"a": 1}) == '{"a": 1}'
    assert f.json_loads('{"a": 1}') == {"a": 1}


def test_toml():
    assert f.toml({"a": 1}) == "a = 1\n"
    assert f.toml_dumps({"a": 1}) == "a = 1\n"
    assert f.toml_dumps({"a": None}) == 'a = "null"\n'
    assert f.toml_loads("a = 1") == {"a": 1}
    assert f.toml_loads('a = "null"') == {"a": None}


def test_read(tmp_path):
    file = tmp_path / "a"
    file.write_text("123")
    assert f.read(file) == "123"


def test_readlines(tmp_path):
    file = tmp_path / "a"
    file.write_text("123\n456")
    assert f.readlines(file) == ["123", "456"]


def test_glob(tmp_path):
    file1 = tmp_path / "a.txt"
    file2 = tmp_path / "b.txt"
    file1.write_text("")
    file2.write_text("")
    assert list(f.glob(tmp_path, "*.txt")) == [str(file1), str(file2)]


def test_glob0(tmp_path):
    file1 = tmp_path / "a.txt"
    file2 = tmp_path / "b.txt"
    file1.write_text("")
    file2.write_text("")
    assert f.glob0(tmp_path, "*.txt") == str(file1)


def test_as_path(tmp_path):
    assert f.as_path(str(tmp_path)) == tmp_path


def test_config(tmp_path):
    conf = tmp_path / "config.toml"
    conf.write_text("a = 1")
    out = f.config(conf)
    assert out == {"a": 1}

    conf = tmp_path / "config"
    conf.write_text("a = 1")
    out = f.config(conf, loader="toml")
    assert out == {"a": 1}

    out = f.config("a = 1", loader="toml")
    assert out == {"a": 1}

    out = f.config('{"a": 1}', loader="json")
    assert out == {"a": 1}

    with pytest.raises(ValueError):
        f.config("a = 1")

    assert f.config({"a": 1}) == {"a": 1}


# path stat
def test_isdir(tmp_path):
    d = tmp_path / "d"
    assert f.isdir(d) is False
    d.mkdir()
    assert f.isdir(d) is True


def test_islink(tmp_path):
    target = tmp_path / "a"
    source = tmp_path / "b"
    source.write_text("")
    target.symlink_to(source)
    assert f.islink(target) is True
    assert f.islink(source) is False


def test_isfile_exists_getsize_and_time(tmp_path):
    fi = tmp_path / "f"
    assert f.isfile(fi) is False
    assert f.exists(fi) is False
    assert f.getsize(fi) == -1
    assert f.getmtime(fi) == -1
    assert f.getctime(fi) == -1
    assert f.getatime(fi) == -1
    fi.write_text("123")
    assert f.isfile(fi) is True
    assert f.exists(fi) is True
    assert f.getsize(fi) == 3
    assert f.getmtime(fi) > 0
    assert f.getctime(fi) > 0
    assert f.getatime(fi) > 0


def test_isempty(tmp_path):
    fi = tmp_path / "f"
    assert f.isempty(fi) is False
    assert f.isempty(fi, nonfile_as_empty=True) is True

    fi.write_text("\n")
    assert f.isempty(fi) is True
    assert f.isempty(fi, ignore_ws=False) is False


def test_regex_replace():
    assert f.regex_replace("a", "a", "b") == "b"
    assert f.regex_replace("a", "a", "b", count=1) == "b"
    assert f.regex_replace("a", "a", "b", flags=0) == "b"
    assert f.regex_replace("a1b2c3", r"(\d+)", "x\\1") == "ax1bx2cx3"
