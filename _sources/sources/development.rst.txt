===========
Development
===========

This package is developed using `poetry <https://python-poetry.org/>`_ which manages the development environment and
python virtualenv for you. It is also used for dependency management, as a development script runner, and packaging.

Initial setup
=============

1. Install a python interpreter for `python >= 3.12`. `pyenv <https://github.com/pyenv/pyenv>`_ is a good choice to do this.
2. Install `poetry <https://python-poetry.org/>`_ (=>1.2.0) globally (i.e. not in a project virtualenv).
3. Run `poetry install` in the project root to create a virtualenv and install all development dependencies.
4. Run `poetry run pre-commit install` in the project root. This will install `git hooks <https://git-scm.com/docs/githooks>`_ to enforce certain code quality requirements prior to committing changes to git.

Development Cycle
=================

During the development process, the code should be linted and type checked. This can be achieved using the following commands:

- For formatting & import sorting: `poetry run poe format`
- For linting: `poetry run poe lint`
- For type checking: `poetry run poe mypy`
- For testing: `poetry run poe test`
- To build the documentation: `poetry run poe docs` (Meaningful ocumentation is not yet included but is TBD.)

Each of these steps should be performed prior to creating a pull request. They can be executed all-at-once by executing
```shell
$ poetry run poe precommit
```
