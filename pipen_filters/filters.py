"""Provides the filters"""
import json
from glob import glob as pyglob
from os import PathLike, path, readlink
from typing import Any, List, Union, Dict, Callable


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
FILTERS["joinpaths"] = path.join
FILTERS["json"] = json.dumps
FILTERS["read"] = read
FILTERS["readlines"] = readlines
FILTERS["glob"] = lambda *paths: list(sorted(pyglob(path.join(*paths))))
FILTERS["glob0"] = lambda *paths: FILTERS["glob"](*paths)[0]
