import tomllib
from pathlib import Path

import context_engine


def test_package_version_matches_pyproject():
    pyproject = tomllib.loads((Path(__file__).parents[1] / "pyproject.toml").read_text())
    assert context_engine.__version__ == pyproject["project"]["version"]


def test_the_spec_names_the_framework_version_the_engine_implements():
    # DEC-19/DEC-23: a framework bump moves the engine's major.minor, the contract's pin and the spec's own banner together
    import re

    spec = (Path(__file__).parents[1] / "docs" / "framework" / "FRAMEWORK.md").read_text(encoding="utf-8")
    want = ".".join(context_engine.__version__.split(".")[:2])
    assert re.findall(r"\bFramework (\d+\.\d+)\b", spec.split("\n\n", 2)[1]) == [want], "FRAMEWORK.md's banner names the framework version"
