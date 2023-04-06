# AppStore

AppStore

## Installation

```bash
pip install appstore
```

## Usage

```python
>>> from appstore import fib
>>> fib(0)
0

```

For more details, read the
[documentation](https://91nunocosta.github.io/appstore/appstore.html).

## Development

### Preparing the development environment

If you want to test or change the source code, prepare your local environment.

1. Clone the repository.

   ```bash
   git clone git@github.com:91nunocosta/appstore.git
   ```

2. Open the project directory.

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
   poetry install --with dev
   ```

5. Enter the virtual environment.

   ```bash
   poetry shell
   ```

6. Install pre-commit verifications.

   ```bash
   pre-commit install -t pre-commit -t pre-push -t commit-msg
   ```

### Pre-commit

Pre-commit runs the linters and tests configured in
[.pre-commit-config.yaml](./.pre-commit-config.yaml).
You can check the _pre-commit_ phase locally:

1. Prepare the development environment, as described in
[**Preparing the development environment**](#preparing-the-development-environment).

2. Run pre-commit with all files.

```bash
pre-commit run --all-files
```

### Tests

Tests are executed by [tox.ini](./tox.ini).
You can check the _tox_ phase locally:

1. Prepare the development environment, as described in
[**Preparing the development environment**](#preparing-the-development-environment).

2. Run tox.

```bash
tox
```
