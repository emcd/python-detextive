# Change: Update UTF BOM provenance reporting

## Why
`detextive` currently handles UTF-8 BOM reporting better after recent fixes, but
the broader UTF-16/UTF-32 families still need an explicit, cross-surface policy
for provenance and consistency. Downstream systems that round-trip text to disk
need deterministic BOM semantics for correctness.

## What Changes
- Add explicit UTF BOM provenance requirements for charset reporting.
- Require consistent charset normalization semantics across decode, detection,
  and inference surfaces.
- Add `Behaviors.utf_16_32_requires_byte_order` to control handling of BOM-less
  generic `utf-16` and `utf-32` trials:
  - `False` (default): preserve current permissive behavior for compatibility.
  - `True`: require explicit byte order for BOM-less UTF-16/32 content (BOM or
    explicit-endianness codec names), avoiding ambiguous native-endian trials.
- Define phased delivery:
  - Phase 1: reporting semantics improvements with no result-struct changes.
  - Phase 2: decode-path hardening for BOM-less UTF-16/UTF-32 handling behind
    `utf_16_32_requires_byte_order`.
  - Phase 3: decision and implementation (if needed) of explicit BOM metadata
    for round-trip fidelity in API results.

## Impact
- Affected specs:
  - `charset-detection`
  - `api`
- Affected code (anticipated):
  - `sources/detextive/charsets.py`
  - `sources/detextive/core.py`
  - `sources/detextive/detectors.py`
  - `sources/detextive/decoders.py`
  - `sources/detextive/inference.py`
  - `tests/test_000_detextive/test_220_charsets.py`
  - `tests/test_000_detextive/test_310_detectors.py`
  - `tests/test_000_detextive/test_400_inference.py`
  - `tests/test_000_detextive/test_500_decoders.py`
  - `documentation/examples/basic-usage.rst`
  - `documentation/examples/advanced-configuration.rst`
