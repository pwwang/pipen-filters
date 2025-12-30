"""Provides the filters"""

from __future__ import annotations

import json
from functools import wraps
from os import PathLike, path
from pathlib import Path
from typing import Any, List, Mapping, Union, Dict, Callable

from diot import Diot
from simpleconf import Config
from simpleconf.caster import cast, null_caster
from panpath import PanPath, CloudPath

FILTERS: Dict[str, Callable] = {}


def add_filter(
    aliases: str | list[str] | Callable | None = None,
) -> Callable[[Callable], Callable]:
    """Add a filter to the FILTERS

    Examples:
        Filters added: `myfilter`
        >>> @add_filter
        ... def myfilter(var):
        ...     return var

        >>> @add_filter()
        ... def myfilter(var):
        ...     return var

        Filters added: `myfilter`, `myfilter2`
        >>> @add_filter("myfilter2")
        ... def myfilter(var):
        ...     return var

    Args:
        aliases: The aliases of the filter, the filter itself, or None

    Returns:
        The filter itself if used directly `@add_filter`; or
        The decorator to add the filter if used with arguments `@add_filter(...)`
    """
    if callable(aliases):
        return add_filter()(aliases)

    aliases = aliases or []
    if isinstance(aliases, str):
        aliases = [aliases]

    def _add_filter(func: Callable) -> Callable:
        FILTERS[func.__name__] = func
        for alias in aliases:
            FILTERS[alias] = func
        return func

    return _add_filter


def _neg1_if_error(func: Callable) -> Callable:
    """Return -1 if an error occurs"""

    @wraps(func)
    def _func(*args: Any, **kwargs: Any) -> int:
        try:
            return func(*args, **kwargs)
        except Exception:
            return -1

    return _func


def _splitexit(
    pth: str | PathLike, ignore: list[str] | str, recursive: bool
) -> tuple[str, str]:
    """Split the extension with leading dot of a file

    Args:
        pth: The path to the file
        ignore: The extensions to ignore
            The extensions can be with or without leading dot
        recursive: Recursively ignore the extensions from the end

    Returns:
        The path and the extension (with leading dot)
    """
    if isinstance(ignore, str):
        ignore = [ignore]

    ignore = ["." + ext.lstrip(".") for ext in ignore]
    pth, last = path.splitext(str(pth))
    if not recursive:
        return (pth, last) if last not in ignore else path.splitext(pth)

    while last in ignore:
        pth, last = path.splitext(pth)
    return pth, last


@add_filter
def realpath(pth: str | PathLike) -> str:
    """Get the real path of a path

    Args:
        pth: The path to the file

    Returns:
        The real path of the file
    """
    return str(PanPath(pth).resolve())


@add_filter
def readlink(pth: str | PathLike) -> str:
    """Get the link of a symlink

    Args:
        pth: The path to the symlink

    Returns:
        The link of the symlink
    """
    return str(PanPath(pth).readlink())


@add_filter
def commonprefix(*paths: str | PathLike, basename_only: bool = True) -> str:
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
    paths = [PanPath(pth).name if basename_only else str(pth) for pth in paths]
    return path.commonprefix(paths)


@add_filter
def dirname(pth: str | PathLike) -> str:
    """Get the directory name of a path

    For example, `/a/b/c.txt => /a/b/`

    Args:
        pth: The path to the file

    Returns:
        The directory name of the file
    """
    return str(PanPath(pth).parent)


@add_filter
def basename(pth: str | PathLike) -> str:
    """Get the basename of a path

    For example, `/a/b/c.txt => c.txt`

    Args:
        pth: The path to the file

    Returns:
        The basename of the file
    """
    return str(PanPath(pth).name)


@add_filter("suffix")
def ext(
    pth: str | PathLike,
    ignore: list[str] | str = [],
    recursive: bool = False,
) -> str:
    """Get the extension of a file

    For example, `/a/b/c.txt => .txt`.

    Aliases: `suffix`

    Args:
        pth: The path to the file
        ignore: The extensions to ignore
            The extensions can be with or without leading dot
        recursive: Recursively ignore the extensions from the end

    Returns:
        The extension of the file
    """
    return _splitexit(pth, ignore, recursive)[1]


@add_filter("suffix0")
def ext0(
    pth: str | PathLike,
    ignore: list[str] | str = [],
    recursive: bool = False,
) -> str:
    """Get the extension of a file without the leading dot

    For example, `/a/b/c.txt => txt`.

    Aliases: `suffix0`

    Args:
        pth: The path to the file
        ignore: The extensions to ignore
            The extensions can be with or without leading dot
        recursive: Recursively ignore the extensions from the end

    Returns:
        The extension of the file without the leading dot
    """
    return ext(pth, ignore, recursive)[1:]


@add_filter
def prefix(
    pth: str | PathLike,
    ignore: list[str] | str = [],
    recursive: bool = False,
) -> str:
    """Get the prefix of a file

    For example, `/a/b/c.txt => /a/b/c`

    Args:
        pth: The path to the file
        ignore: The extensions to ignore
            The extensions can be with or without leading dot
        recursive: Recursively ignore the extensions from the end

    Returns:
        The prefix of the file
    """
    return _splitexit(pth, ignore, recursive)[0]


@add_filter
def prefix0(
    pth: str | PathLike,
    ignore: list[str] | str = [],
    recursive: bool = False,
) -> str:
    """Get the prefix of a file without the extension

    For example, `/a/b/c.d.txt => /a/b/c.d`

    Args:
        pth: The path to the file
        ignore: The extensions to ignore
            The extensions can be with or without leading dot
        recursive: Recursively ignore the extensions from the end

    Returns:
        The prefix of the file without the extension
    """
    return str(PanPath(pth).parent / FILTERS["filename0"](pth, ignore, recursive))


@add_filter(["fn", "stem"])
def filename(
    pth: str | PathLike,
    ignore: list[str] | str = [],
    recursive: bool = False,
) -> str:
    """Get the filename of a file.

    For example, `/a/b/c.d.txt => c.d`.

    Aliases: `fn`, `stem`

    Args:
        pth: The path to the file
        ignore: The extensions to ignore
            The extensions can be with or without leading dot
        recursive: Recursively ignore the extensions from the end

    Returns:
        The filename of the file
    """
    return basename(_splitexit(pth, ignore, recursive)[0])


@add_filter(["fn0", "stem0"])
def filename0(
    pth: str | PathLike,
    ignore: list[str] | str = [],
    recursive: bool = False,
) -> str:
    """Get the filename of a file without the extension

    For example, `/a/b/c.d.txt => c`.

    Aliases: `fn0`, `stem0`

    Args:
        pth: The path to the file
        ignore: The extensions to ignore
            The extensions can be with or without leading dot
        recursive: Recursively ignore the extensions from the end

    Returns:
        The filename of the file without the extension
    """
    return filename(pth, ignore, recursive).split(".")[0]


@add_filter("joinpath")
def joinpaths(pathsegment: str | PathLike, *pathsegments: str | PathLike) -> str:
    """Join paths.

    For example, `joinpaths("a", "b") => "a/b"`.

    Aliases: `joinpath`

    Args:
        pathsegment: The path to join
        *pathsegments: The paths to join

    Returns:
        The joined path
    """
    return str(PanPath(pathsegment).joinpath(*pathsegments))


@add_filter
def as_path(pth: str | PathLike) -> Path | CloudPath:
    """Convert a path to a Path object

    Args:
        pth: The path to convert

    Returns:
        The Path object
    """
    return PanPath(pth)


@add_filter
def isdir(pth: str | PathLike) -> bool:
    """Check if a path is a directory

    Args:
        pth: The path to check

    Returns:
        True if the path is a directory, False otherwise
    """
    return PanPath(pth).is_dir()


@add_filter
def isfile(pth: str | PathLike) -> bool:
    """Check if a path is a file

    Args:
        pth: The path to check

    Returns:
        True if the path is a file, False otherwise
    """
    return PanPath(pth).is_file()


@add_filter
def islink(pth: str | PathLike) -> bool:
    """Check if a path is a symlink

    Args:
        pth: The path to check

    Returns:
        True if the path is a symlink, False otherwise
    """
    return PanPath(pth).is_symlink()


@add_filter
def exists(pth: str | PathLike) -> bool:
    """Check if a path exists

    Args:
        pth: The path to check

    Returns:
        True if the path exists, False otherwise
    """
    return PanPath(pth).exists()


@add_filter
@_neg1_if_error
def getsize(pth: str | PathLike) -> int:
    """Get the size of a file, return -1 if the file does not exist

    Args:
        pth: The path to the file

    Returns:
        The size of the file
    """
    return PanPath(pth).stat().st_size


@add_filter
@_neg1_if_error
def getmtime(pth: str | PathLike) -> int:
    """Get the modification time of a file, return -1 if the file does not exist

    Args:
        pth: The path to the file

    Returns:
        The modification time of the file
    """
    return PanPath(pth).stat().st_mtime


@add_filter
@_neg1_if_error
def getctime(pth: str | PathLike) -> int:
    """Get the creation time of a file, return -1 if the file does not exist

    Args:
        pth: The path to the file

    Returns:
        The creation time of the file
    """
    return PanPath(pth).stat().st_ctime


@add_filter
@_neg1_if_error
def getatime(pth: str | PathLike) -> int:
    """Get the access time of a file, return -1 if the file does not exist

    Args:
        pth: The path to the file

    Returns:
        The access time of the file
    """
    return PanPath(pth).stat().st_atime


@add_filter
def isempty(
    pth: str | PathLike,
    ignore_ws: bool = True,
    nonfile_as_empty: bool = False,
) -> bool:
    """Check if a file is empty

    Args:
        pth: The path to the file
        ignore_ws: Ignore whitespaces?
        nonfile_as_empty: Treat non-file as empty?

    Returns:
        True if the file is empty, False otherwise
    """
    pth = PanPath(pth)
    if not pth.is_file():
        return nonfile_as_empty

    if not ignore_ws:
        return getsize(pth) == 0

    return pth.read_text().strip() == ""


@add_filter
def quote(var: Any, quote_none: bool = False) -> str:
    """Quote a string

    Args:
        var: The string to quote
        quote_none: Quote None as '"None"'?
            Otherwise, return 'None', without quotes

    Returns:
        The quoted string
    """
    if var is None and not quote_none:
        return 'None'

    return json.dumps(str(var))


@add_filter
def squote(var: Any, quote_none: bool = False) -> str:
    """Quote a string with single quotes

    Args:
        var: The string to quote
        quote_none: Quote None as "'None'"?
            Otherwise, return 'None', without quotes

    Returns:
        The quoted string
    """
    if var is None and not quote_none:
        return 'None'

    return repr(str(var))


@add_filter("json")
def json_dumps(var: Any) -> str:
    """Dump an object to json.

    Aliases: `json`

    Args:
        var: The object to dump

    Returns:
        The json string
    """
    return json.dumps(var)


@add_filter
def json_load(pth: str | PathLike) -> Any:
    """Load a json file

    Args:
        pth: The path to the json file

    Returns:
        The loaded object
    """
    return config(pth, "json")


@add_filter
def json_loads(jsonstr: str) -> Any:
    """Load a json string to an object

    Args:
        jsonstr: The json string

    Returns:
        The loaded object
    """
    return json.loads(jsonstr)


@add_filter("toml_dumps")
def toml(var: Any) -> str:
    """Dump an object to toml.

    Aliases: `toml_dumps`

    Args:
        var: The object to dump

    Returns:
        The toml string
    """
    return Diot(var).to_toml()


@add_filter
def toml_load(pth: str | PathLike) -> Any:
    """Load a toml file. `null` will be loaded as None

    Args:
        pth: The path to the toml file

    Returns:
        The loaded object
    """
    return config(pth, "toml")


@add_filter
def toml_loads(tomlstr: str) -> Any:
    """Load a toml string to an object, `null` will be loaded as None

    Args:
        tomlstr: The toml string

    Returns:
        The loaded object
    """
    return cast(Config.load(tomlstr, loader="tomls"), [null_caster])


@add_filter
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

    if isinstance(x, str) and not PanPath(x).is_file():
        if loader == "toml":
            return Diot(FILTERS["toml_loads"](x))
        if loader == "json":
            return Diot(FILTERS["json_loads"](x))
        raise ValueError(f"Unknown loader: {loader}")

    return Config.load_one(x, loader=loader)


@add_filter
def glob(pathsegment: str | PathLike, *pathsegments: str | PathLike) -> List[str]:
    """Glob a path

    Args:
        pathsegment: The path to glob
        *pathsegments: The paths to glob

    Returns:
        The globbed paths
    """
    return list(
        sorted([str(p) for p in PanPath(pathsegment).glob("/".join(pathsegments))])
    )


@add_filter
def glob0(*paths: str | PathLike) -> str:
    """Glob a path and return the first result

    Args:
        *paths: The paths to glob

    Returns:
        The first globbed path
    """
    return glob(*paths)[0]


@add_filter
def read(file: str | PathLike, *args: Any, **kwargs: Any) -> Union[str, bytes]:
    """Read the contents from a file

    Args:
        file: The path to the file
        *args: and
        **kwargs: Other arguments passed to `open()`

    Returns:
        The contents of the file
    """
    with PanPath(file).open(*args, **kwargs) as fvar:
        return fvar.read()


@add_filter
def readlines(
    file: str | PathLike,
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


@add_filter
def regex_replace(
    string: str,
    pattern: str,
    repl: str,
    count: int = 0,
    flags: int = 0,
) -> str:
    """Replace the matched pattern with a string

    Args:
        string: The string to search
        pattern: The pattern to search
        repl: The string to replace
        flags: The regex flags

    Returns:
        The replaced string
    """
    import re

    return re.sub(pattern, repl, string, count=count, flags=flags)


@add_filter
def slugify(string: str, *args: Any, **kwargs: Any) -> str:
    """Slugify a string

    Args:
        string: The string to slugify
        *args: and
        **kwargs: Other arguments to `slugify()`

    Returns:
        The slugified string
    """
    from slugify import slugify as _slugify

    return _slugify(string, *args, **kwargs)
