"""Validate the Snap packaging recipe and its README documentation.

The snap is not built in CI (snapcraft needs LXD and is slow), so these tests
guard the recipe's structure and the install docs against silent typos that
would break the certbot content-interface wiring.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
SNAPCRAFT_PATH = ROOT / "snap" / "snapcraft.yaml"
README_PATH = ROOT / "README.rst"


@pytest.fixture(scope="module")
def snapcraft() -> dict:
    assert SNAPCRAFT_PATH.is_file(), f"{SNAPCRAFT_PATH} does not exist"
    data = yaml.safe_load(SNAPCRAFT_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "snapcraft.yaml must parse to a mapping"
    return data


def test_snap_metadata_follows_certbot_convention(snapcraft: dict) -> None:
    assert snapcraft.get("name") == "certbot-dns-arsys"
    assert snapcraft.get("confinement") == "strict"
    assert snapcraft.get("grade") == "stable"
    assert str(snapcraft.get("base", "")).startswith("core")


def test_snap_has_python_part_from_repo(snapcraft: dict) -> None:
    parts = snapcraft.get("parts")
    assert isinstance(parts, dict) and parts, "parts must be a non-empty mapping"
    python_parts = [
        p
        for p in parts.values()
        if isinstance(p, dict) and p.get("plugin") == "python" and p.get("source") == "."
    ]
    assert python_parts, "expected a python plugin part sourced from the repo root '.'"


def test_snap_wires_certbot_content_interface(snapcraft: dict) -> None:
    slots = snapcraft.get("slots")
    assert isinstance(slots, dict), "slots must be a mapping"
    content_slots = [
        s
        for s in slots.values()
        if isinstance(s, dict)
        and s.get("interface") == "content"
        and s.get("content") == "certbot-1"
    ]
    assert content_slots, "expected a content slot advertising 'certbot-1'"

    plugs = snapcraft.get("plugs")
    assert isinstance(plugs, dict), "plugs must be a mapping"
    meta = plugs.get("certbot-metadata")
    assert isinstance(meta, dict), "expected a 'certbot-metadata' plug"
    assert meta.get("interface") == "content"
    assert meta.get("content") == "metadata-1"
    assert meta.get("default-provider") == "certbot"


def test_readme_documents_snap_install() -> None:
    text = README_PATH.read_text(encoding="utf-8")
    assert "\nSnap\n" in text, "README must have a 'Snap' section heading"
    assert "snap install certbot-dns-arsys" in text
    assert "snap connect" in text
