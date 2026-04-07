# Copilot / AI assistant instructions for this repository

This file gives focused, actionable guidance for AI coding agents working in this repository.

- **Project layout:** small Python package at the workspace root.
  - Key files: `main.py` (simple CLI entrypoint), `pyproject.toml` (package metadata), `README.md` (currently empty).
  - Python requirement: `>=3.12` (from `pyproject.toml`).

- **Big picture:**
  - This repository currently contains a minimal API package (single-module). There is no web framework or service scaffolding present.
  - Typical change scope is small: edit `main.py` for behavior, update `pyproject.toml` to add dependencies/metadata, and add modules as needed.

- **How to run locally:**
  - Run the CLI entrypoint during development: `python main.py` (from the repo root).
  - Packaging and publishing follow standard `pyproject.toml` flows (PEP 621 style). No build scripts or CI config are present.

- **Development conventions discovered here:**
  - Keep the package top-level simple—single `main.py` currently acts as the user-facing entrypoint.
  - Add new modules as sibling files and import them from `main.py` (no package init required yet).

- **When editing code:**
  - Prefer small, self-contained changes. If adding runtime dependencies, also update `pyproject.toml` `dependencies` section.
  - Example: to add `requests` add `requests = "^<version>"` to `dependencies` in `pyproject.toml`.

- **Testing & CI:**
  - No tests or CI configuration detected. If adding tests, follow pytest conventions (create a `tests/` folder and use `pytest`), and add `pytest` to `pyproject.toml` if needed.

- **Patterns & examples from repository:**
  - Entrypoint pattern: `if __name__ == "__main__": main()` in `main.py` — preserve this pattern when adding CLI behavior.
  - Use `pyproject.toml` for metadata; do not create setup.py unless necessary for backward compatibility.

- **Integration points & external dependencies:**
  - None currently configured; external integrations should be explicit in `pyproject.toml` and documented in `README.md`.

- **Safety and scope rules for AI completions:**
  - Do not assume additional services (databases, web servers) exist unless new files/configs are added.
  - When proposing new high-level architecture (APIs, services), include minimal runnable code + updated `pyproject.toml` + README usage instructions.

- **If you add CI or GH workflows:**
  - Place workflows under `.github/workflows/` and reference `python -m pytest` or `python -m build` as steps. Document new workflows in `README.md`.

- **What to ask the human developer:**
  - Where should new modules live (root vs package)?
  - Preferred testing framework and CI provider, if any.

If anything here is unclear or you want more detail (tests, CI, packaging examples), tell me which area to expand.
