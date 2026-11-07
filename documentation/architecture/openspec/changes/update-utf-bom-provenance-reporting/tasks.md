## 1. Specification and design
- [x] 1.1 Confirm UTF BOM provenance policy for UTF-16 and UTF-32 label
      reporting, including BOM-present vs BOM-absent behavior.
- [x] 1.2 Confirm whether BOM provenance requires explicit API metadata
      (`DecodeInformResult` field) or can remain fully encoded in charset labels
      for the targeted use cases.

## 2. Phase 1 implementation (no result-struct changes)
- [x] 2.1 Extend charset normalization logic to recognize UTF-16/UTF-32 BOM
      bytes for reporting decisions.
- [x] 2.2 Apply shared normalization consistently across decode, detection, and
      inference paths.
- [x] 2.3 Add and update tests for UTF-8/16/32 BOM provenance across
      `decode_inform`, detection, and inference.

## 3. Phase 2 implementation (decode-path hardening)
- [x] 3.1 Add `Behaviors.utf_16_32_requires_byte_order` (default `False`) and
      document semantics for permissive vs strict BOM-less generic UTF-16/32
      handling.
- [x] 3.2 Tighten BOM-less generic UTF-16/UTF-32 decode trial behavior only
      when `utf_16_32_requires_byte_order` is enabled, to avoid ambiguous
      platform-endian outcomes.
- [x] 3.3 Add tests for both modes:
      - default permissive compatibility behavior
      - strict mode BOM-less generic UTF-16/32 handling
      - explicit-endianness codec reporting in strict mode

## 4. Phase 3 optional API enhancement (DEFERRED)
Decision (2026-11-07): defer explicit BOM metadata. Charset labels already
encode BOM presence (`utf-8-sig`, generic-vs-explicit UTF-16/32 families),
which the consulted downstream consumer (mimeogram, via owner consult)
confirmed sufficient for label-driven write-back (`content.encode(charset)`
of new content, never byte-verbatim restore). Labels do NOT preserve
byte-exact round-trip fidelity: BOM-bearing UTF-16LE and UTF-16BE both
normalize to generic `utf-16`, losing original byte order. Reopen if a
consumer requires byte-exact BOM/order write-back metadata.
- [ ] 4.1 If required by round-trip clients, add explicit BOM metadata to
      `DecodeInformResult` (and related documentation) in an additive manner.
      (Deferred — see decision above.)
- [ ] 4.2 Add tests demonstrating round-trip preservation behavior for BOM
      write-back workflows. (Not applicable while deferred.)

## 5. Validation and documentation
- [x] 5.1 Run linters and targeted pytest suites for charset, detector,
      inference, and decoder modules.
- [x] 5.2 Run documentation doctests and update examples to match final
      semantics.

## 6. Threshold regression assurance
- [x] 6.1 Add deterministic threshold tests (stubbed detectors, no live
      backends): trial-decode admission below/at/above confidence.
- [x] 6.2 Cover text-validation boundaries (AsNeeded below/above threshold,
      Always, Never).
- [x] 6.3 Cover strict/permissive BOM-less generic handling, explicit
      endianness, BOM-bearing paths, and the BOM-stripped text invariant.
