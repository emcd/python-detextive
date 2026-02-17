## 1. Specification and design
- [ ] 1.1 Confirm UTF BOM provenance policy for UTF-16 and UTF-32 label
      reporting, including BOM-present vs BOM-absent behavior.
- [ ] 1.2 Confirm whether BOM provenance requires explicit API metadata
      (`DecodeInformResult` field) or can remain fully encoded in charset labels
      for the targeted use cases.

## 2. Phase 1 implementation (no result-struct changes)
- [ ] 2.1 Extend charset normalization logic to recognize UTF-16/UTF-32 BOM
      bytes for reporting decisions.
- [ ] 2.2 Apply shared normalization consistently across decode, detection, and
      inference paths.
- [ ] 2.3 Add and update tests for UTF-8/16/32 BOM provenance across
      `decode_inform`, detection, and inference.

## 3. Phase 2 implementation (decode-path hardening)
- [ ] 3.1 Review and tighten BOM-less UTF-16/UTF-32 decode trial behavior to
      avoid ambiguous platform-endian outcomes.
- [ ] 3.2 Add tests for BOM-less UTF-16/UTF-32 edge cases and explicit
      endianness codec reporting.

## 4. Phase 3 optional API enhancement
- [ ] 4.1 If required by round-trip clients, add explicit BOM metadata to
      `DecodeInformResult` (and related documentation) in an additive manner.
- [ ] 4.2 Add tests demonstrating round-trip preservation behavior for BOM
      write-back workflows.

## 5. Validation and documentation
- [ ] 5.1 Run linters and targeted pytest suites for charset, detector,
      inference, and decoder modules.
- [ ] 5.2 Run documentation doctests and update examples to match final
      semantics.
