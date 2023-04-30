# App Store

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Lint codebase](https://github.com/91nunocosta/store/actions/workflows/lint.yml/badge.svg)](https://github.com/91nunocosta/store/actions/workflows/lint.yml)
[![Run tests](https://github.com/91nunocosta/store/actions/workflows/test.yml/badge.svg)](https://github.com/91nunocosta/store/actions/workflows/test.yml)

Proof of Concept (PoC) for a mobile app store controller, supporting _sell_ operation.

## Installation

```bash
pip install -e git+ssh://git@github.com/91nunocosta/store.git#egg=appstore
```

## Usage

Enter the `appstore` _Read-Eval-Print Loop (REPL) Command Line Interface (CLI)_,
and type `help`.

<!-- markdownlint-disable line-length -->

```
appstore
>help
```
<!-- markdownlint-enable line-length -->

## Documentation

See the internal API's documentation [here](https://91nunocosta.github.io/store/).

The implementation includes the following classes:

![UML Classes Diagram](./classes.svg)

## Next steps

The PoC focuses on app sales business logic, implemented in [`appstore`](./appstore/appstore.py)
module.

In a real world-scenario, some steps would likely follow:

1. Implementing app persistence and distributed access.
I.e., providing an `AppsDB` interface connected to a database.

2. Implementing user persistence and distributed access.
I.e., providing an `UsersDB` interface connected to a database.
There could be a combination of DBMS.
We could keep the purchases counter in a key-value memory DB as Redis.

3. Implementing a full-fledged `AccountsController`.
It likely implies connecting to external services.
Such services could support functionalities such as currency exchange.
They could accept accounts in many currencies and perform the _transferences_ accordingly.

## Development

### Preparing the development environment

If you want to test or change the source code, prepare your local environment.

1. Clone the repository.

   ```bash
   git clone git@github.com:91nunocosta/store.git
   ```

2. Change to the project directory.

   ```bash
   cd appstore
   ```

3. Install [_poetry_](https://python-poetry.org/) _package and dependency manager_.
Follow the [poetry installation guide](https://python-poetry.org/docs/#installation).
Chose the method that is more convenient to you, for example:

   ```bash
   curl -sSL\
        https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py \
      | python -
   ```

4. Create a new virtual environment (managed by _poetry_) with the project dependencies.

   ```bash
   poetry install --with lint --with test --with cd
   ```

5. Activate the virtual environment.

   ```bash
   poetry shell
   ```

### Pre-commit

Pre-commit runs the linters configured in
[.pre-commit-config.yaml](./.pre-commit-config.yaml).

You can run it as follows:

1. Prepare the development environment, as described in
[**Preparing the development environment**](#preparing-the-development-environment).

2. Run pre-commit with all files.

```bash
pre-commit run --all-files
```

### Tests

You can execute all tests and test coverage with [tox.ini](./tox.ini).

1. Prepare the development environment, as described in
[**Preparing the development environment**](#preparing-the-development-environment).

2. Run tox.

```bash
tox
```
