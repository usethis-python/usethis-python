# File Manager

The File Manager pattern is a core part of how usethis reads and writes configuration
files. It provides a consistent, safe abstraction over file I/O that ensures changes are
applied efficiently and without leaving files in a partial state.

## Motivation

usethis often needs to make multiple changes to the same file in a single operation.
For example, when adding a tool it might add a dependency entry, set lint rules, and
configure paths — all in `pyproject.toml`. Without a dedicated abstraction, this would
mean reading the file multiple times (once per change) and writing it multiple times
(once per change), which is both slow and risky: if a write fails halfway through, the
file is left in an inconsistent state.

The File Manager approach solves this by buffering all reads and writes through an
in-memory cache: the file is read at most once, all changes are applied to the
in-memory copy, and the result is written back to disk exactly once when the context
exits. This is what the codebase calls _deferred writes_ or _atomic writes_.

The performance benefit is measurable: a speedup of up to 30% has been observed in
situations that involve many changes to a single YAML file.

## Class Hierarchy

The hierarchy is defined in `src/usethis/_io.py` and the `src/usethis/_file/` package.

```
UsethisFileManager[DocumentT]         (src/usethis/_io.py)
└── KeyValueFileManager[DocumentT]    (src/usethis/_io.py)
    ├── TOMLFileManager               (src/usethis/_file/toml/io_.py)
    │   ├── PyprojectTOMLManager      (src/usethis/_file/pyproject_toml/io_.py)
    │   ├── UVTOMLManager             (src/usethis/_backend/uv/toml.py)
    │   ├── DotCoverageRCTOMLManager  (src/usethis/_config_file.py)
    │   ├── DotRuffTOMLManager        (src/usethis/_config_file.py)
    │   └── RuffTOMLManager           (src/usethis/_config_file.py)
    ├── YAMLFileManager               (src/usethis/_file/yaml/io_.py)
    │   ├── MkDocsYMLManager          (src/usethis/_config_file.py)
    │   ├── BitbucketPipelinesYAMLManager  (src/usethis/_integrations/ci/bitbucket/yaml.py)
    │   └── PreCommitConfigYAMLManager    (src/usethis/_integrations/pre_commit/yaml.py)
    └── INIFileManager                (src/usethis/_file/ini/io_.py)
        ├── SetupCFGManager           (src/usethis/_file/setup_cfg/io_.py)
        ├── DotCodespellRCManager     (src/usethis/_config_file.py)
        ├── DotCoverageRCManager      (src/usethis/_config_file.py)
        ├── DotImportLinterManager    (src/usethis/_config_file.py)
        ├── DotPytestINIManager       (src/usethis/_config_file.py)
        ├── PytestINIManager          (src/usethis/_config_file.py)
        └── ToxINIManager             (src/usethis/_config_file.py)
```

`UsethisFileManager` is the abstract root and handles locking, caching, and I/O
scheduling. `KeyValueFileManager` extends it with key-path operations
(`set_value`, `extend_list`, `remove_from_list`, etc.) used by all config formats.
The three format-specific managers (`TOMLFileManager`, `YAMLFileManager`,
`INIFileManager`) implement parsing and serialisation using `tomlkit`,
`ruamel.yaml`, and `configupdater` respectively, each preserving comments and
formatting. Concrete managers such as `PyprojectTOMLManager` simply provide the
`relative_path` property and may re-wrap exceptions with more specific types.

## The Context Manager Pattern

Every file manager is used as a context manager:

```python
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager

with PyprojectTOMLManager() as manager:
    manager.set_value(keys=["tool", "ruff", "line-length"], value=120, exists_ok=True)
    manager.extend_list(keys=["tool", "ruff", "lint", "select"], values=["A"])
# File is written to disk here, once, on __exit__.
```

The lifecycle is:

1. **`__enter__`** — calls `lock()`, which registers the file path in the shared
   `_content_by_path` dictionary (see [Locking](#locking) below). Raises
   `UnexpectedFileOpenError` if the same file is already open in another instance.
2. **`get()`** — on first call, reads the file from disk and caches the parsed
   document. Subsequent calls return the cached copy without touching the disk.
3. **`commit(document)`** — replaces the cached document with a new version (called
   internally by `set_value`, `extend_list`, etc.).
4. **`write_file()`** — serialises the in-memory document and writes it back to disk.
   If `get()` was never called (i.e. no reads or writes happened), nothing is written.
   If the file was deleted during the context, nothing is written.
5. **`__exit__`** — calls `write_file()` then `unlock()`, which removes the path from
   `_content_by_path`.

All mutations within a single `with` block are therefore collapsed into a single
disk read and a single disk write, regardless of how many individual operations are
performed.

## Locking

The locking mechanism prevents two instances of the same manager from operating on the
same file simultaneously, which would cause one to overwrite the other's changes.

```python
# Class-level dictionary shared across all instances
_content_by_path: ClassVar[dict[Path, DocumentT | None]] = {}
```

A file is considered _locked_ when its absolute path is present as a key in
`_content_by_path`. The value is `None` when the file has been locked but not yet read,
and the parsed document otherwise.

Because `_content_by_path` is a class variable on `UsethisFileManager`, it is shared
across the entire process — not just across instances of the same subclass. This means
that, for example, `PyprojectTOMLManager` and a hypothetical second `TOMLFileManager`
subclass pointing to the same path cannot both be open at the same time.

## The `files_manager()` Composite Context Manager

`src/usethis/_config_file.py` provides a convenience context manager that opens all
known config file managers at once:

```python
from usethis._config_file import files_manager

with files_manager():
    # All supported config files are now locked and ready for deferred writes.
    ...
```

This is used when a command might touch many different configuration files, so that
every file touched within the block benefits from deferred writes and none is written
more than once. The composite manager simply nests all the individual managers using
Python's `with (A(), B(), C(), ...)` syntax.

## Adding a New File Manager

To manage a new configuration file:

1. Choose the appropriate base class for the file format (`TOMLFileManager`,
   `YAMLFileManager`, or `INIFileManager`).
2. Subclass it, providing a `relative_path` property that returns the path of the
   file relative to the current project directory.
3. Add the new manager to `files_manager()` in `src/usethis/_config_file.py`.

```python
# src/usethis/_config_file.py

class MyConfigManager(TOMLFileManager):
    """Manages myconfig.toml."""

    @property
    def relative_path(self) -> Path:
        return Path("myconfig.toml")
```

If the new format is not TOML, YAML, or INI, you can instead subclass
`KeyValueFileManager` directly and implement `_parse_content` and `_dump_content`
to handle parsing and serialisation.
