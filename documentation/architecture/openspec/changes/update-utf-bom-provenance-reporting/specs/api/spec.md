## ADDED Requirements

### Requirement: BOM-Semantics Separation
The system SHALL separate BOM provenance reporting semantics from decoded-text
transformation semantics.

Priority: High

#### Scenario: remove_bom does not alter reported provenance
- **WHEN** callers toggle `remove_bom` behavior for the same UTF input bytes
- **THEN** decoded text transformation follows `remove_bom`
- **AND** reported charset provenance remains tied to source-byte BOM state

### Requirement: Decode/Inference Provenance Consistency
The system SHALL provide consistent UTF BOM provenance reporting across
high-level decode and inference APIs.

Priority: High

#### Scenario: decode_inform and infer_mimetype_charset agreement
- **WHEN** callers provide identical content and contextual hints to
  `decode_inform` and MIME/charset inference APIs
- **THEN** returned charset metadata agrees on UTF BOM provenance semantics

### Requirement: BOM Round-Trip Extensibility
The system SHALL support an additive path to explicit BOM metadata for API
results when charset labels alone are insufficient for downstream round-trip
fidelity.

Priority: Medium

#### Scenario: Round-trip client requires explicit BOM metadata
- **WHEN** a client must preserve and later reapply BOM state independently of
  decoded text
- **THEN** the API can expose explicit BOM metadata without breaking existing
  callers
