import pytest

from pipen_filters.filters import FILTERS

globals().update(FILTERS)


def test_realpath(tmp_path):
    target = tmp_path / "a"
    source = tmp_path / "b"
    source.write_text("")
    target.symlink_to(source)
    assert realpath(target) == str(source)


def test_slugify():
    assert slugify("a b") == "a-b"


def test_readlink(tmp_path):
    target = tmp_path / "a"
    source = tmp_path / "b"
    source.write_text("")
    target.symlink_to(source)
    assert readlink(target) == str(source)


def test_dirname():
    assert dirname("/a/b") == "/a"


def test_basename():
    assert basename("/a/b/c.txt") == "c.txt"


def test_commonprefix():
    assert commonprefix("/a/b/abc.txt", "/a/b/abc.png") == "abc."
    assert (
        commonprefix("/a/b/abc.txt", "/a/b/abc.png", basename_only=False)
        == "/a/b/abc."
    )


def test_ext():
    assert ext("/a/b.txt") == ".txt"


def test_ext0():
    assert ext0("/a/b.txt") == "txt"


def test_prefix():
    assert prefix("/a/b.c.txt") == "/a/b.c"


def test_prefix0():
    assert prefix0("/a/b.c.txt") == "/a/b"


def test_filename():
    assert filename("/a/b.c.txt") == "b.c"


def test_filename0():
    assert filename0("/a/b.c.txt") == "b"


def test_quote():
    assert quote("1") == '"1"'


def test_squote():
    assert squote("1") == "'1'"


def test_joinpaths():
    assert joinpaths("a", "b") == "a/b"


def test_json():
    assert json({"a": 1}) == '{"a": 1}'
    assert json_dumps({"a": 1}) == '{"a": 1}'
    assert json_loads('{"a": 1}') == {"a": 1}


def test_toml():
    assert toml({"a": 1}) == "a = 1\n"
    assert toml_dumps({"a": 1}) == "a = 1\n"
    assert toml_dumps({"a": None}) == 'a = "null"\n'
    assert toml_loads("a = 1") == {"a": 1}
    assert toml_loads('a = "null"') == {"a": None}


def test_read(tmp_path):
    file = tmp_path / "a"
    file.write_text("123")
    assert read(file) == "123"


def test_readlines(tmp_path):
    file = tmp_path / "a"
    file.write_text("123\n456")
    assert readlines(file) == ["123", "456"]


def test_glob(tmp_path):
    file1 = tmp_path / "a.txt"
    file2 = tmp_path / "b.txt"
    file1.write_text("")
    file2.write_text("")
    assert list(glob(tmp_path, "*.txt")) == [str(file1), str(file2)]


def test_glob0(tmp_path):
    file1 = tmp_path / "a.txt"
    file2 = tmp_path / "b.txt"
    file1.write_text("")
    file2.write_text("")
    assert glob0(tmp_path, "*.txt") == str(file1)


def test_as_path(tmp_path):
    assert as_path(str(tmp_path)) == tmp_path


def test_config(tmp_path):
    conf = tmp_path / "config.toml"
    conf.write_text("a = 1")
    out = config(conf)
    assert out == {"a": 1}

    conf = tmp_path / "config"
    conf.write_text("a = 1")
    out = config(conf, loader="toml")
    assert out == {"a": 1}

    out = config("a = 1", loader="toml")
    assert out == {"a": 1}

    out = config('{"a": 1}', loader="json")
    assert out == {"a": 1}

    with pytest.raises(ValueError):
        config("a = 1")

    assert config({"a": 1}) == {"a": 1}
