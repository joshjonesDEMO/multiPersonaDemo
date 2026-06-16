# multiPersonaDemo

This repository contains a single static HTML document, `multiPersonalDemo.html` — the "Cursor Demo Playbook — Four Personas, One Story" GTM playbook. It is a self-contained page (inline CSS, no JavaScript, no external assets) with in-page anchor navigation between persona sections.

## Cursor Cloud specific instructions

- This repo is a **static site with no dependencies, no package manager, and no build step**. There is nothing to install, compile, or bundle.
- There is no lint, test, or build tooling configured (no `package.json`, `Makefile`, linter configs, or test suites). Treat lint/test/build as N/A unless tooling is later added.
- To run/preview the playbook, serve the repo root with any static file server and open `multiPersonalDemo.html`, e.g. `python3 -m http.server 8080 --directory /workspace` then visit `http://localhost:8080/multiPersonalDemo.html`. `python3` and `node` are available in the environment.
- The page is fully static (no `<script>`); the only interactivity is the sticky top nav, which jumps to in-page anchors (`#story`, `#sa`, `#de`, `#po`, `#dev`, `#flow`, `#tips`). Editing the file is reflected on a simple browser refresh — no rebuild needed.
