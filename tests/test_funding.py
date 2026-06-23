"""Validate the GitHub FUNDING.yml sponsorship configuration.

GitHub silently ignores a malformed ``.github/FUNDING.yml``, so these tests
guard the file against typos that would quietly hide the "Sponsor" button.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

FUNDING_PATH = Path(__file__).resolve().parent.parent / ".github" / "FUNDING.yml"

# Recognized GitHub funding platforms (top-level keys allowed in FUNDING.yml).
RECOGNIZED_PLATFORMS = {
    "github",
    "patreon",
    "open_collective",
    "ko_fi",
    "tidelift",
    "community_bridge",
    "liberapay",
    "issuehunt",
    "lfx_membership",
    "polar",
    "buy_me_a_coffee",
    "thanks_dev",
    "custom",
}


@pytest.fixture(scope="module")
def funding() -> dict:
    assert FUNDING_PATH.is_file(), f"{FUNDING_PATH} does not exist"
    data = yaml.safe_load(FUNDING_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "FUNDING.yml must parse to a mapping"
    return data


def test_funding_declares_github_sponsor(funding: dict) -> None:
    assert "github" in funding, "FUNDING.yml must declare a 'github' channel"
    value = funding["github"]
    names = value if isinstance(value, list) else [value]
    assert "spanishkangaroo" in names, "github channel must name 'spanishkangaroo'"


def test_funding_uses_only_recognized_platforms(funding: dict) -> None:
    unknown = set(funding) - RECOGNIZED_PLATFORMS
    assert not unknown, f"Unrecognized funding platform keys: {sorted(unknown)}"
