---
troy-doc: "ADR-0006"
lang: "en"
version: "1.0"
updated: "2026-11-10"
status: "Approved by Troy on 2026-11-10"
mirror: "ADR-0006-install-with-uv-tool.zh-CN.md"
---

# ADR-0006: Install recipe-menu with uv tool

## 1. Status

Accepted. Troy accepted it on 2026-11-10 by approving `docs/architecture.md`.

## 2. Context

`recipe-menu` must run from any folder in PowerShell, and the architecture says how Troy installs it (requirements 7). troy-mode's Python rule allows no `.venv` folder, and the development environment is a mamba environment whose code changes with every branch that Troy or troy-mode checks out. uv is already in that environment. The repository is `git@github.com:ZJUCao/recipe-menu.git`, and troy-mode creates a GitHub release with a tag such as `v0.1.0` when Troy accepts a version.

## 3. Decision

F05 declares the console script `recipe-menu = "recipe_menu.cli:main"` in `pyproject.toml`. To install an accepted version, Troy runs these commands once, in a PowerShell where uv is available, such as the activated development environment:

```text
uv tool install --managed-python --python 3.13 "git+ssh://git@github.com/ZJUCao/recipe-menu.git@v0.1.0"
uv tool update-shell
```

The first command builds the tool's own environment, with a Python that uv manages, and puts `recipe-menu.exe` in uv's folder for tool commands. The second command adds that folder to Troy's PATH. A new PowerShell then finds `recipe-menu` in every folder. To move to a newer version, Troy runs the first command again with the new tag and `--force`. To try `main` before a release, Troy runs it with `--force` and the repository folder in place of the Git address, from a clean checkout of `main`.

## 4. Options considered

| Option | Pros | Cons |
| --- | --- | --- |
| `uv tool install` from a release tag | uv is already there. The tool has its own environment and Python, so changes to the development environment or a branch never break the installed command. A tag installs exactly what Troy accepted. | The first install downloads a Python and the build backend. Updating needs one command. |
| An editable install in the development environment, plus a PowerShell profile function | No second environment. | The command runs whatever branch is checked out, including a mock that raises on every call. It works only after the environment is activated, or through a profile change. |
| pipx | A known tool for this. | One more tool to install, which uv already replaces. |
| A single executable built with PyInstaller | No Python needed at all. | A new build dependency, a large file, and a build step for every release. |

## 5. Consequences

- The installed command is "usable on Troy's devices" only from the version that Troy installs, which matches the status labels of R13.
- Installation uses the network once, to fetch the code, a Python, and hatchling. The tool itself never does.
- The version test plan includes installing the release this way on Troy's PC and running `recipe-menu --version` in Windows PowerShell 5.1 and PowerShell 7.

## 6. Related

- Features: F05
- Rules: R13
