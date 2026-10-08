import tomllib
from pathlib import Path

import context_engine


def test_package_version_matches_pyproject():
    pyproject = tomllib.loads((Path(__file__).parents[1] / "pyproject.toml").read_text())
    assert context_engine.__version__ == pyproject["project"]["version"]
