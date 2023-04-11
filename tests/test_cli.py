"""Test the command line interface for app store's purchases manager."""
import io
import os
from pathlib import Path
from typing import Iterable

import pytest

from appstore.cli import run


def _get_input_files() -> Iterable[Path]:
    _dir = Path(__file__).parent / "cli"
    return _dir.glob("input*.txt")


def _test_id(input_file: Path) -> str:
    return input_file.stem


def _output_file(input_file: Path) -> Path:
    name = input_file.name.replace("input", "output")
    return input_file.with_name(name)


@pytest.mark.parametrize("input_file", argvalues=_get_input_files(), ids=_test_id)
def test_cli(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    input_file: Path,
) -> None:
    """Tests command line interface.

    Args:
        monkeypatch: Pytest patch fixture.
        capsys: Pytest fixture for accessing stdout.
        input_file: Text file to use as stdin.
    """
    monkeypatch.setattr("sys.stdin", input_file.open())
    run()
    captured = capsys.readouterr()
    assert captured.out.strip() == _output_file(input_file).read_text().strip()


def test_wrong_ids(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Tests inputing wrong ids in the CLI.

    Args:
        monkeypatch: Pytest patch fixture.
        capsys: Pytest fixture for accessing stdout.
    """
    commands = [
        "sell WrongApp Oil User#123",
        "sell TrivialDrive WrongItem User#123",
        "sell TrivialDrive Oil WrongUser",
        "exit",
    ]
    stdin = os.linesep.join(commands)
    monkeypatch.setattr("sys.stdin", io.StringIO(stdin))
    run()
    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        ">Couldn't find Oil!",
        ">Couldn't find WrongItem!",
        ">Couldn't find WrongUser!",
        ">",
    ]


def test_forbidden_debit(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Tests triggering forbidden debits from the CLI.

    Args:
        monkeypatch: Pytest patch fixture.
        capsys: Pytest fixture for capturing the stdout and stderr.
    """
    commands = ["sell TrivialDrive Oil User#123" for _ in range(11)]
    commands.append("exit")
    stdin = os.linesep.join(commands)
    monkeypatch.setattr("sys.stdin", io.StringIO(stdin))
    run()
    captured = capsys.readouterr()
    # For now, we assume that if the user doesn't have an account, it's balance is 0.
    assert "Can't sell an app" in captured.out


def test_invalid_commands(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Tests inputing wrong commands in the CLI.

    Args:
        monkeypatch: Pytest patch fixture.
        capsys: Pytest fixture for capturing the stdout and stderr.
    """
    commands = [
        "wrong command",
        "exit",
    ]
    stdin = os.linesep.join(commands)
    monkeypatch.setattr("sys.stdin", io.StringIO(stdin))
    run()
    captured = capsys.readouterr()
    assert "Supported commands:" in captured.out
