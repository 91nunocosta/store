"""Test the command line interface for appstore."""
from typer.testing import CliRunner

from appstore.cli import app

runner = CliRunner()


def test_app() -> None:
    """Test the command line interface for appstore"""
    result = runner.invoke(app, ["10"])
    assert result.exit_code == 0
    assert result.stdout.strip() == "55"
