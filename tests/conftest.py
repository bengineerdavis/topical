"""Fixtures for the topical generator suite.

The subject is the `topical` package itself — tests run under `uv run
--group test pytest`, which syncs the project (editable) plus the test
group into the environment. The scaffold source (`--repo`) is a
SYNTHETIC
fleet checkout: a tmp dir holding a small dotfiles/managers.yaml that
covers every manager class (package with and without vars, outline,
Debian-only). The skeleton is not fixtured — it ships in the package and
is part of what the tests exercise.
"""

from __future__ import annotations

import pytest
import topical.cli

REPO = __import__("pathlib").Path(__file__).resolve().parents[1]

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
def fleet_repo(tmp_path_factory):
    """A synthetic fleet checkout: dotfiles/managers.yaml only."""
    fleet = tmp_path_factory.mktemp("fleet")
    dotfiles = fleet / "dotfiles"
    dotfiles.mkdir()
    (dotfiles / "managers.yaml").write_text(SYNTHETIC_MANAGERS, encoding="utf-8")
    return fleet


@pytest.fixture()
def runner():
    from typer.testing import CliRunner

    return CliRunner()


@pytest.fixture()
def scaffold(runner, fleet_repo, tmp_path):
    """Invoke `topical new` into tmp_path; return (result, into)."""

    def _scaffold(*args: str) -> tuple:
        result = runner.invoke(
            topical.cli.app,
            ["new", *args, "--repo", str(fleet_repo), "--into", str(tmp_path)],
        )
        return result, tmp_path

    return _scaffold
