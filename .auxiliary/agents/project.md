# Project Guidance

Project-owned knowledge the generated `AGENTS.md` entrypoint must not own.
Structured tracking stays in `nb`.

## Purpose

Detextive is a Python library for consolidated text detection: MIME type
detection (magic bytes with extension fallback), charset detection
(statistical analysis with UTF-8 optimization), line-separator processing
(CR/LF/CRLF), and textual-content validation. Used by downstream Python
applications to detect encoding, MIME type, newlines, and textuality for
files and byte buffers.

## Tech Stack

Python >= 3.12 (CPython 3.12 through 3.15); Hatch build and envs; runtime deps
accretive, chardet, puremagic, typing-extensions, absence, dynadoc, frigid
with optional charset-normalizer and python-magic extras; QA via pytest,
pyright, ruff, isort, sphinx, towncrier, vulture.

## Notes

<!-- Accumulate project-specific knowledge, constraints, deviations, and durable
     links here. For structured items, use `nb`.

     Migration: if upgrading from an AGENTS.md that still had inline Purpose,
     Tech Stack, or Project Notes sections, move that body here once, then accept
     the template-owned AGENTS.md pointer.

     TODO: If this project uses multiple agent/clone roles, create a stable
     team-organization note in `nb`, modeled after one of the examples at:
     https://raw.githubusercontent.com/emcd/agents-common/master/examples/nb-notes/team-organization/README.md
     Then link the note here, for example:
     - Team org, role ownership, signoff policy, and merge workflow: `coordination/general/<n>` -->
