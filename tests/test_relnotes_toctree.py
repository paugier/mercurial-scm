"""Tests of the table of contents of the release notes."""

from relnotes_toctree import sorted_versions, split_versions


def test_sorted_versions():
    names = ["6.9", "7.0", "6.10", "archive", "7.0.1", "index"]
    assert sorted_versions(names) == ["7.0.1", "7.0", "6.10", "6.9"]


def test_split_versions():
    names = ["6.8", "7.1", "6.9", "7.0"]
    assert split_versions(names, 3) == (["7.1", "7.0", "6.9"], ["6.8"])
    assert split_versions(names, 10) == (["7.1", "7.0", "6.9", "6.8"], [])
