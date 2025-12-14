# Line Separator Processing

## Purpose
This capability detects and normalizes line separators to ensure consistent text processing across different platforms (Windows, macOS, Linux).

## Requirements

### Requirement: Separator Detection
The system SHALL detect line separator types (CR, LF, CRLF) from byte or text content.

Priority: Critical

#### Scenario: Detect CRLF
- **WHEN** content containing `\r\n` is analyzed
- **THEN** the system identifies the separator as CRLF

### Requirement: Normalization to Unix
The system SHALL normalize line endings to Unix LF (`\n`) format for internal processing consistency.

Priority: Critical

#### Scenario: Normalize text
- **WHEN** text with mixed or non-Unix line endings is processed
- **THEN** all line separators are converted to `\n`

### Requirement: Platform Conversion
The system SHALL support converting line endings to platform-specific formats when needed for output.

Priority: Critical

#### Scenario: Convert to Windows
- **WHEN** text needs to be saved for Windows
- **THEN** `\n` characters are converted to `\r\n`
