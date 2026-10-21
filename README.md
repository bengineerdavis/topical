# topical

Manager for topic-structured chezmoi-Ansible dotfiles repos.

A topic is a self-contained Ansible role with metadata (`topic.yml`),
lifecycle stubs, a standalone playbook and a changelog. `topical new`
creates one that is correct for the package managers it declares — the
cask playbook vars for a cask topic, `become: true` for apt, and nothing
for managers the topic does not use. More verbs land over time; the
design is in `dotfiles/docs/ROADMAP-topic-cli.md`.

## Install

```bash
uv tool install git+https://github.com/bengineerdavis/topical
```

On the author's fleet the `apps/topical` topic owns this. PyPI
publication is queued once the CLI surface settles.

## Usage

```bash
topical new firefox --os Darwin --requires homebrew --manager homebrew_cask
topical new my-tool --os Darwin --os Debian --manager homebrew_formula
```

Run from inside the target repo (discovery walks upward for
`dotfiles/managers.yaml`), or pass `--repo /path/to/checkout`. The topic
lands in `<repo>/dotfiles/apps/<name>`; `--into DIR` targets a different
layout root, and the generator refuses to overwrite an existing topic.

What remains to edit by hand depends on the manager: nothing for a plain
brew or apt package; the commented outlines for `apt_repository` and
`release_artifact`, whose URLs, keys and checksums are per-topic and
unknowable to a generator.

## Where what lives

| Piece | Home | Why |
|---|---|---|
| `src/topical/template/` | this repo | the canonical topic skeleton: manager-neutral, shipped as package data, copied and marker-spliced |
| `src/topical/cli.py` | this repo | the generator: block templates and the package/outline mode map |
| `managers.yaml` | the target repo (`dotfiles/`) | fleet data: module, become, OS coverage, playbook vars, upgraded_by, per-manager traps |

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

## Development

```bash
uv run topical --help          # run the editable package
uv run --group test pytest tests -q
```

The suite drives the Typer app in-process against a synthetic
`dotfiles/managers.yaml` fixture covering every manager class; the
in-package skeleton is exercised as-is. New tests are not finished until
seen to fail against a deliberately broken generator — the commits carry
`Mutation:`/`Failing-test:` trailers.

## License

MIT — see LICENSE.md.
