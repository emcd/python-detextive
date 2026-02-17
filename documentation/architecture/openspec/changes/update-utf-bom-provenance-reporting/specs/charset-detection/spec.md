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
