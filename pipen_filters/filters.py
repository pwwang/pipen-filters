"""Provides the filters"""
import json
import tempfile
from glob import glob as pyglob
from os import PathLike, path, readlink
from pathlib import Path
from typing import Any, List, Mapping, Union, Dict, Callable

import rtoml
from diot import Diot
from simpleconf import Config
from simpleconf.exceptions import FormatNotSupported
from simpleconf.caster import cast, null_caster
from slugify import slugify  # type: ignore


def commonprefix(*paths: PathLike, basename_only: bool = True) -> str:
    """Get the common prefix of a set of paths

    Examples:
        >>> commonprefix("/a/b/abc.txt", "/a/b/abc.png")
        >>> # "abc."
        >>> commonprefix("/a/b/abc.txt", "/a/b/abc.png", basename_only=False)
        >>> # "/a/b/abc."

    Args:
        *paths: The paths to find commonprefix agaist
        basename_only: Only search on the basenames

    Returns:
        The common prefix of the paths
    """
    paths = [path.basename(pth) if basename_only else pth for pth in paths]
    return path.commonprefix(paths)


def config(x: Any, loader: str = None) -> Mapping[str, Any]:
    """Get the configuration (python dictionary) from a file

    Args:
        x: The path to the file, dict or string of configurations (json or toml)
        loader: The loader to use, defaults to auto-detect
            If x is a dict, this argument is ignored
            if x is a string and is not a file path, then x will be loaded as
            a toml string if loader is not specified
            if x is a file path, then x will be loaded according to the file
            extension

    Returns:
        The config
    """
    if not isinstance(x, (Path, str)):  # assume dict
        return Config.load_one(x, loader="dict")

    if isinstance(x, str) and not Path(x).is_file():
        if loader == "toml":
            return Diot(FILTERS["toml_loads"](x))
        if loader == "json":
            return Diot(FILTERS["json_loads"](x))
        raise ValueError(f"Unknown loader: {loader}")

    return Config.load_one(x, loader=loader)


def read(file: PathLike, *args: Any, **kwargs: Any) -> Union[str, bytes]:
    """Read the contents from a file

    Args:
        file: The path to the file
        *args: and
        **kwargs: Other arguments passed to `open()`

    Returns:
        The contents of the file
    """
    with open(file, *args, **kwargs) as fvar:
        return fvar.read()


def readlines(
    file: PathLike,
    *args: Any,
    **kwargs: Any,
) -> Union[List[str], List[bytes]]:
    """Read the lines from a file

    Args:
        file: The path to the file
        *args: and
        **kwargs: Other arguments to `open()`

    Returns:
        A list of lines in the file
    """
    return read(file, *args, **kwargs).splitlines()


FILTERS: Dict[str, Callable] = {}
FILTERS["realpath"] = path.realpath
FILTERS["readlink"] = readlink
# /a/b/c.txt => /a/b/
FILTERS["dirname"] = path.dirname
# /a/b/c.txt => c.txt
FILTERS["basename"] = path.basename
FILTERS["commonprefix"] = commonprefix
# /a/b/c.txt => .txt
FILTERS["ext"] = lambda pth: path.splitext(pth)[-1]
# /a/b/c.txt => txt
FILTERS["ext0"] = lambda pth: FILTERS["ext"](pth).lstrip(".")
# /a/b/c.d.e.txt => /a/b/c.d.e
FILTERS["prefix"] = lambda pth: path.splitext(pth)[0]
# /a/b/c.d.e.txt => c.d.e
FILTERS["filename"] = lambda pth: path.basename(FILTERS["prefix"](pth))
FILTERS["fn"] = FILTERS["filename"]
FILTERS["stem"] = FILTERS["filename"]
# /a/b/c.d.e.txt => c
FILTERS["filename0"] = lambda pth: FILTERS["filename"](pth).split(".")[0]
FILTERS["fn0"] = FILTERS["filename0"]
FILTERS["stem0"] = FILTERS["filename0"]
# /a/b/c.d.e.txt => /a/b/c
FILTERS["prefix0"] = lambda pth: path.join(
    path.dirname(pth), FILTERS["fn0"](pth)
)
FILTERS["quote"] = lambda var: json.dumps(str(var))
FILTERS["squote"] = lambda var: repr(str(var))
FILTERS["slugify"] = slugify
FILTERS["joinpaths"] = path.join
FILTERS["json"] = json.dumps
FILTERS["json_dumps"] = json.dumps
FILTERS["json_load"] = lambda x: config(x, "json")
FILTERS["json_loads"] = json.loads
FILTERS["toml"] = rtoml.dumps
FILTERS["toml_dumps"] = rtoml.dumps
# Able to load "null" as None
FILTERS["toml_load"] = lambda x: config(x, "toml")
FILTERS["toml_loads"] = lambda tomlstr: cast(
    Diot(rtoml.loads(tomlstr)),
    [null_caster],
)
FILTERS["read"] = read
FILTERS["readlines"] = readlines
FILTERS["glob"] = lambda *paths: list(sorted(pyglob(path.join(*paths))))
FILTERS["glob0"] = lambda *paths: FILTERS["glob"](*paths)[0]
FILTERS["as_path"] = Path
FILTERS["config"] = config
