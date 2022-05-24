# pipen-filters

Add a set of useful filters for [pipen][1] templates.

These filters can be used for both liquid and jinja2 templating in pipen.

## Installation

```
pip install -U pipen-filters
```

## Enabling/Disabling the plugin

The plugin is registered via entrypoints. It's by default enabled. To disable it:
`plugins=[..., "no:filters"]`, or uninstall this plugin.

## Usage

```python
from pipen import Proc

class MyProc(Proc):
    input = "infile:file"
    output = "outfile:file:{{in.infile | stem}}.txt"
    ...
```

## Filters

- Parse the symbolic links

    - `realpath`: `os.path.realpath`
    - `readlink`: `os.readlink`

- Find common prefix of given paths

    - `commonprefix`:

        ```python
        >>> commonprefix("/a/b/abc.txt", "/a/b/abc.png")
        >>> # "abc."
        >>> commonprefix("/a/b/abc.txt", "/a/b/abc.png", basename_only=False)
        >>> # "/a/b/abc."
        ```

- Get parts of the path

    - `dirname`: `path.dirname`
    - `basename`: `path.basename`
    - `ext`: get the extension (`/a/b/c.txt -> .txt`)
    - `ext0`: get the extension without dot (`/a/b/c.txt -> txt`)
    - `prefix`: get the prefix of a path (`/a/b/c.d.txt -> /a/b/c.d`)
    - `prefix0`: get the prefix of a path without dot in basename (`/a/b/c.d.txt -> /a/b/c`)
    - `filename`, `fn`, `stem`: get the stem of a path (`/a/b.c.txt -> b.c`)
    - `filename0`, `fn0`, `stem0`: get the stem of a path without dot (`/a/b.c.txt -> b`)
    - `joinpaths`: join path parts (`os.path.join`)
    - `as_path`: convert a string into a `pathlib.Path` object

- Quote data

    - `quote`: put double quotes around data (`1 -> "1"`)
    - `squote`: put single quotes around data (`1 -> '1'`)

- Configurations
    - `json`: `json.dumps`
    - `json_dump`: Load json froma  file
    - `json_dumps`: Alias of `json`
    - `json_loads`: `json.loads`
    - `toml`: `toml.dumps`
    - `toml_dump`: Load toml from a file
    - `toml_dumps`: Alias of `toml`
    - `toml_loads`: `toml.loads`
    - `config`: Load configuration from an object, a string or a file

- Globs

    - `glob`: Like `glob.glob`, but allows passing multiple parts of a path
    - `glob0`: Like `glob`, but only returns the first matched path

- Read file contents

    - `read`: Read file content. You can also pass arguments to `open`
    - `readlines`: Read file content as a list of lines. Additional arguments will be passed to `open`


[1]: https://github.com/pwwang/pipen
