"""The skeleton only ever scaffolds the zsh layout that actually loads.

`.zshrc` sources `apps/<topic>/files/zsh/*.zsh` and nothing else. If
template/ drifts into emitting fragments anywhere else, every generated
topic starts with dead copies — see tests/topics/test_zsh_layout.py in
the dotfiles repo for the incident history (52 dead files; sourced
2-3x before the glob was narrowed). That suite guards the topics;
this one guards the scaffold they come from.
"""

from __future__ import annotations

from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / "template"


def test_skeleton_emits_zsh_only_under_files_zsh():
    assert TEMPLATE.is_dir(), f"skeleton missing at {TEMPLATE}"
    stray = sorted(TEMPLATE.glob("*.zsh")) + sorted((TEMPLATE / "zsh").glob("*.zsh"))
    assert not stray, (
        "the skeleton scaffolds zsh fragments outside files/zsh/, so every "
        "generated topic starts with dead copies:\n  "
        + "\n  ".join(str(p) for p in stray)
    )


def test_skeleton_keeps_the_five_lifecycle_files():
    """Every topic must ship all five; the skeleton is their source."""
    tasks = TEMPLATE / "tasks"
    for name in ("bootstrap", "prerequisites", "install", "remove", "upgrade", "main"):
        assert (tasks / f"{name}.yaml").is_file(), f"template/tasks/{name}.yaml missing"


def test_skeleton_carries_the_splice_markers_the_generator_reads():
    """Marker drift makes `topical new` fail 'skeleton has drifted'."""
    for relpath, marker in (
        ("tasks/install.yaml", "# __MANAGER_BLOCKS__"),
        ("tasks/remove.yaml", "# __MANAGER_BLOCKS__"),
        ("playbook.yaml", "# __PLAYBOOK_VARS__"),
    ):
        text = (TEMPLATE / relpath).read_text(encoding="utf-8")
        assert marker in text, f"{marker!r} missing from template/{relpath}"
