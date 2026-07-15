"""Smoke test: the package imports and exposes a version.

Placeholder so the lint/type/test CI gate is green from the foundation (S001)
onward. Real ingestion tests arrive with S003.
"""

from nfl import __version__


def test_version_is_exposed() -> None:
    assert __version__ == "0.1.0"
