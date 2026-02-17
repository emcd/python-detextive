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

## 4. Phase 3 optional API enhancement
- [ ] 4.1 If required by round-trip clients, add explicit BOM metadata to
      `DecodeInformResult` (and related documentation) in an additive manner.
- [ ] 4.2 Add tests demonstrating round-trip preservation behavior for BOM
      write-back workflows.

## 5. Validation and documentation
- [x] 5.1 Run linters and targeted pytest suites for charset, detector,
      inference, and decoder modules.
- [ ] 5.2 Run documentation doctests and update examples to match final
      semantics.
