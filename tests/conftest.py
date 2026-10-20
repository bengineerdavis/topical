"""Fixtures for the topical generator suite.

The subject is ./topical at the repo root — no .py extension, so it
loads
through SourceFileLoader. The scaffold source (`--repo`) is a SYNTHETIC
fleet checkout: a tmp dir holding a small dotfiles/managers.yaml that
covers every manager class (package with and without vars, outline,
Debian-only). The skeleton is not fixtured — it ships with the tool
and is
part of what the tests exercise.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOPICAL_PATH = REPO / "topical"

# A minimal fleet catalog covering every emission path: package managers
# with and without playbook vars, a tap, a Debian-only manager, and both
# outline managers. Mirrors dotfiles/managers.yaml's schema, not rows.
SYNTHETIC_MANAGERS = """\
version: 1

playbook_var_defs:
  homebrew_prefix: >-
    {{ '/opt/homebrew' if ansible_facts['architecture'] == 'arm64' else '/usr/local' }}
  user_appdir: >-
    {{ ansible_facts['env']['HOME'] }}/Applications

managers:

  homebrew_formula:
    module: community.general.homebrew
    used_by: 1
    playbook_vars: []
    become: false
    upgraded_by: system_role
    os: [Darwin, Debian]
    notes: synthetic fixture row.

  homebrew_cask:
    module: community.general.homebrew_cask
    used_by: 1
    playbook_vars: [homebrew_prefix, user_appdir]
    become: false
    upgraded_by: system_role
    os: [Darwin]
    notes: synthetic fixture row.

  homebrew_tap:
    module: community.general.homebrew_tap
    used_by: 1
    playbook_vars: []
    become: false
    upgraded_by: system_role
    os: [Darwin, Debian]
    notes: synthetic fixture row.

  apt:
    module: ansible.builtin.apt
    used_by: 1
    playbook_vars: []
    become: true
    upgraded_by: system_role
    os: [Debian]
    notes: synthetic fixture row.

  apt_repository:
    module: ansible.builtin.deb822_repository
    used_by: 1
    playbook_vars: []
    become: true
    upgraded_by: system_role
    os: [Debian]
    notes: synthetic fixture row.

  release_artifact:
    module: ansible.builtin.get_url
    used_by: 1
    playbook_vars: []
    become: false
    upgraded_by: topic
    os: [Darwin, Debian]
    notes: synthetic fixture row.
"""


@pytest.fixture(scope="session")
def topical_module():
    """Import ./topical as a module so tests can drive its Typer app."""
    if not TOPICAL_PATH.exists():
        pytest.skip(f"topical source not found at {TOPICAL_PATH}")
    try:
        loader = importlib.machinery.SourceFileLoader("topical", str(TOPICAL_PATH))
        spec = importlib.util.spec_from_loader(
            "topical", loader, origin=str(TOPICAL_PATH)
        )
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        # The script resolves the skeleton as `Path(__file__).parent /
        # "template"`; module_from_spec does not populate __file__ for a
        # SourceFileLoader spec, so set it before exec_module reads it.
        mod.__file__ = str(TOPICAL_PATH)
        loader.exec_module(mod)
        return mod
    except ImportError as exc:
        pytest.skip(f"topical deps not installed ({exc})")


@pytest.fixture(scope="session")
def fleet_repo(tmp_path_factory):
    """A synthetic fleet checkout: dotfiles/managers.yaml only."""
    fleet = tmp_path_factory.mktemp("fleet")
    dotfiles = fleet / "dotfiles"
    dotfiles.mkdir()
    (dotfiles / "managers.yaml").write_text(SYNTHETIC_MANAGERS, encoding="utf-8")
    return fleet


@pytest.fixture()
def runner(topical_module):
    from typer.testing import CliRunner

    return CliRunner()


@pytest.fixture()
def scaffold(runner, fleet_repo, topical_module, tmp_path):
    """Invoke `topical new` into tmp_path; return (result, into)."""

    def _scaffold(*args: str) -> tuple:
        result = runner.invoke(
            topical_module.app,
            ["new", *args, "--repo", str(fleet_repo), "--into", str(tmp_path)],
        )
        return result, tmp_path

    return _scaffold
