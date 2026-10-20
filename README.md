# topical

Manager-aware scaffolder for chezmoi-Ansible topics.

`topical new` creates a topic (an Ansible role with metadata, lifecycle
stubs, a standalone playbook and a changelog) that is correct for the
package managers it declares — the cask playbook vars for a cask topic,
`become: true` for apt, and nothing for managers the topic does not use.

## Usage

```bash
uv run --script ./topical new firefox --os Darwin --requires homebrew --manager homebrew_cask
uv run --script ./topical new my-tool --os Darwin --os Debian --manager homebrew_formula
```

Run from inside the fleet checkout (repo discovery walks upward for
`dotfiles/managers.yaml`), or pass `--repo /path/to/checkout`. The topic
lands in `<repo>/apps/<name>`; `--into DIR` targets a different root, and
the generator refuses to overwrite an existing topic.

What remains to edit by hand depends on the manager: nothing for a plain
brew or apt package; the commented outlines for `apt_repository` and
`release_artifact`, whose URLs, keys and checksums are per-topic and
unknowable to a generator.

## Where what lives

| Piece | Home | Why |
|---|---|---|
| `template/` | this repo | the canonical topic skeleton: manager-neutral, copied verbatim, splice markers replaced |
| `topical` | this repo | the generator: block templates and the package/outline mode map |
| `managers.yaml` | the fleet checkout (`dotfiles/`) | fleet data: module, become, OS coverage, playbook vars, upgraded_by, per-manager traps |

Two emission modes. `package` managers (homebrew_formula, homebrew_cask,
homebrew_tap, apt) produce a complete live block from the topic name.
`outline` managers (apt_repository, release_artifact) produce a commented
skeleton carrying the manager's traps.

## Provenance and destination

Born from the dotfiles repo's TASKS.md A9
(`github.com:bengineerdavis/dotfiles`). The canonical topic skeleton moved
here with the tool on 2026-10-20, by the author's ownership decision: the
template items live in topical first and then in the copier topic-template
repo — sharing one canonical template rather than diverging. This repo is
also the future home of the `topical` agent plugin
(`dotfiles/docs/ROADMAP-topic-cli.md` § Amendment: CLI and plugin ship
from one repository).

## Tests

```bash
uv run --group test pytest tests -q
```

The suite drives the Typer app in-process against a synthetic
`dotfiles/managers.yaml` fixture that covers every manager class; the
skeleton under `template/` is exercised as-is. New tests are not finished
until seen to fail against a deliberately broken generator — the import
commit carries the `Mutation:`/`Failing-test:` trailers.
