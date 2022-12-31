# Windows Support

In order to have the best development experience, the initial, lamest constraint is... that Windows is unsupported, however,
multi-arch will be and Windows should follow, but it is simply not the focus at this time. Contributions welcome.

## Required Software

Binary programs that are required to be on your system:

- `bash`
- `jq`
- `python@3.10` (not literal - just showing required version)

Development libraries that are required to be on your system:

- `GDAL`
- `rasterio`

## Optional

These additional programs can make life easier when you're coding / developing or debugging unit tests.

- `code` (i.e. VSCode IDE)
- `watchman` (optional - debugging support)

## Considerations on Code Organization

- It is acceptable and good practice to put all python code under `src`
- It is better to not add `src/__init__.py` b/c you'll nest `src/tests` and `src/flow` under the same module (making bloated builds)
- You cannot do relative path imports from `src/tests/` to get to `...flow.args`.
- It is possible to use `.env` style way to prepend `PYTHONPATH` for running unit tests, i.e. `"${workspaceFolder}/src/flow"`.
- Special considerations for the PYTHONPATH for unit tests is assumed to be unfavorable if it can be avoided.
