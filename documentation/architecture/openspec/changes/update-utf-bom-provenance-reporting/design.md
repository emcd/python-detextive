## Context
Recent v3 work corrected UTF-8 reporting so charset labels track BOM
provenance rather than `remove_bom` text-shaping behavior. The same clarity is
not yet fully established for UTF-16 and UTF-32 families. Clients such as
`python-mimeogram` need deterministic provenance to preserve or reapply BOMs in
write-back workflows.

## Goals / Non-Goals
- Goals:
  - Define clear UTF BOM provenance semantics across decode, detection, and
    inference APIs.
  - Preserve consistency between surfaces for the same input bytes.
  - Support robust downstream round-trip behavior.
- Non-Goals:
  - Broad charset detection heuristics redesign outside UTF BOM semantics.
  - Introducing breaking API changes in this proposal.

## Decisions
- Decision: Keep a phased implementation strategy.
  - Phase 1: Extend reporting semantics without changing result struct shapes.
  - Phase 2: Harden UTF-16/UTF-32 decode trials where BOM is absent.
  - Phase 3: Add explicit BOM metadata only if charset labels alone are
    insufficient for consumer fidelity requirements.
- Decision: Keep `remove_bom` scoped to decoded text content behavior, not
  provenance reporting.
- Decision: Use a shared normalization path to avoid drift between decoder and
  detector/inference pathways.

## UTF Reporting Policy (Proposed)
- UTF-8:
  - BOM present bytes => report `utf-8-sig`.
  - BOM absent bytes => report `utf-8`.
- UTF-16 and UTF-32 families:
  - BOM present bytes => report canonical BOM-aware family codec (`utf-16` or
    `utf-32`).
  - BOM absent bytes => report explicit endianness codec when known
    (`utf-16-le`, `utf-16-be`, `utf-32-le`, `utf-32-be`), or preserve existing
    explicit codec reporting when decode path already established it.

## Risks / Trade-offs
- Python codec behavior for BOM-less UTF-16/UTF-32 can be platform-sensitive or
  ambiguous with generic family codecs, increasing false positives if not
  constrained.
- Adding explicit BOM metadata increases API surface complexity but can improve
  fidelity for round-trip tools.

## Migration Plan
1. Land Phase 1 semantics and tests first, with no struct shape changes.
2. Evaluate downstream integrations (`python-mimeogram`, `python-librovore`)
   for residual ambiguity.
3. If ambiguity remains, add explicit BOM metadata as an additive API update.

## Resolved Questions
- Explicit BOM metadata scope:
  - Add only to metadata-returning decode surfaces, specifically
    `decode_inform`, if Phase 3 is needed.
  - Do not add BOM metadata to plain-text-only decode APIs.
- Inference metadata scope:
  - `CharsetResult` structures may gain optional BOM metadata in a future
    additive update.
  - Plain charset string reporting semantics remain unchanged by that metadata.
