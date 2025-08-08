# tape-record-helpers

Python script(s) to help with compact cassette recording

## Dependencies

Poetry is used for dependency management.

* [poetry install docs](https://python-poetry.org/docs/#installation)
* [poetry-shell should be installed as well](https://github.com/python-poetry/poetry-plugin-shell)

After that fetch dependencies: `poetry install` and execute scripts in poetry venv via: `poetry shell`.

P.S. Alternatively plain pip could be used with `pip install -r requirements.txt`

### pre-commit hooks

pre-commit hooks are used to improve developer experience by checking for issues before committing them. Install it with `brew install pre-commit` and then enable with `pre-commit install` (once).

## Scripts

### playlist_gen.py

Generates VLC playlist for recording based on input with total duration checks.

Use `./playlist_gen.py -h` for options.
