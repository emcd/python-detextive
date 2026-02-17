## ADDED Requirements

### Requirement: UTF BOM Provenance Reporting
The system SHALL report UTF charset results using source-byte BOM provenance
semantics instead of text-shaping behavior flags.

Priority: Critical

#### Scenario: Report UTF-8 without BOM
- **WHEN** UTF-8 content is decoded or inferred without a UTF-8 BOM prefix
- **THEN** the reported charset is `utf-8`

#### Scenario: Report UTF-8 with BOM
- **WHEN** UTF-8 content is decoded or inferred with a UTF-8 BOM prefix
- **THEN** the reported charset is `utf-8-sig`

#### Scenario: Report UTF-16 or UTF-32 with BOM
- **WHEN** UTF-16 or UTF-32 content includes a corresponding BOM prefix
- **THEN** the reported charset is the canonical BOM-aware family codec
- **AND** the result distinguishes BOM-bearing family content from BOM-less
  explicit-endianness content

### Requirement: UTF Reporting Consistency Across Detection Surfaces
The system SHALL apply the same UTF BOM provenance normalization logic across
detection and inference surfaces.

Priority: High

#### Scenario: Consistent UTF reporting for equivalent inputs
- **WHEN** the same byte content is analyzed through charset detection and
  MIME/charset inference APIs
- **THEN** reported charset names are semantically consistent for BOM
  provenance

### Requirement: Configurable UTF-16/32 Byte-Order Strictness
The system SHALL provide a behavior flag,
`Behaviors.utf_16_32_requires_byte_order`, that controls whether BOM-less
generic `utf-16` and `utf-32` trials are allowed.

Priority: High

#### Scenario: Default compatibility mode remains permissive
- **WHEN** callers do not set `utf_16_32_requires_byte_order`
- **THEN** the default behavior remains permissive for BOM-less generic
  `utf-16` and `utf-32` trials
- **AND** UTF BOM provenance reporting semantics remain unchanged

#### Scenario: Strict mode requires explicit byte order
- **WHEN** `utf_16_32_requires_byte_order` is `True`
- **AND** input bytes are BOM-less
- **AND** the trial codec is generic `utf-16` or generic `utf-32`
- **THEN** that trial is rejected as ambiguous
- **AND** callers must provide BOM-bearing content or explicit-endianness
  codec names (`utf-16-le`, `utf-16-be`, `utf-32-le`, `utf-32-be`)
