# `detextive` Package Development Plan

## 1. Project Goal

Create a new Python package named `detextive` that provides a comprehensive and reliable way to determine the mimetype and charset of files and byte content. The package will also offer utilities for handling HTTP headers and line endings.

## 2. Core Functionality

- Detect mimetype from byte content and/or location (filename/URL).
- Detect charset from byte content.
- Determine if a mimetype is textual.
- Parse mimetype and charset from HTTP `Content-Type` headers.
- Detect, nativize, and normalize line endings.

## 3. API Design

- **`detextive.core`**:
  - `detect_mimetype(content: bytes, location: Location) -> str | None`: The `Location` type will be a union of `str`, `os.PathLike`, and `urllib.parse.ParseResult`.
  - `detect_charset(content: bytes) -> str | None`:
  - `detect_mimetype_and_charset(content: bytes, location: Location) -> tuple[str, str | None]`:
  - `is_textual_mimetype(mimetype: str) -> bool`:
- **`detextive.http`**:
  - `parse_content_type(header: str) -> tuple[str | None, str | None]`: Parses a `Content-Type` header and returns a `(mimetype, charset)` tuple.
- **`detextive.lines`**: (Formerly `detextive.text`)
  - `detect_line_separator(content: bytes) -> str | None`:
  - `nativize_line_separators(content: str) -> str`:
  - `normalize_line_separators(content: str, separator: str = '\n') -> str`:

## 4. Implementation Details

- **Mimetype Detection**:
  - Use `puremagic` as the primary detection library for its ease of bundling.
  - Implement a fallback to the standard library `mimetypes` module if `puremagic` fails or returns a generic result.
  - The `is_textual_mimetype` function will incorporate logic from `originals/acquirers.py`, including checks for textual suffixes (e.g., `+xml`).
- **Charset Detection**:
  - Use the `chardet` library.
  - Retain the logic from `originals/acquirers.py` for handling UTF variants and reducing false positives.
- **Line Ending Handling**:
  - Base the implementation on the `_parts.LineSeparators` class from `mimeogram`, but expose the functionality as simple, module-level functions.
- **Dependencies**:
  - `chardet`
  - `puremagic`

## 5. Development Workflow

1.  Update `pyproject.toml` with the new dependencies (`chardet`, `puremagic`).
2.  Implement the `detextive.exceptions` module.
3.  Implement the `detextive.core` module.
4.  Implement the `detextive.http` module.
5.  Implement the `detextive.lines` module.
6.  Add comprehensive unit tests for all public functions.
7.  Ensure all code adheres to the project's coding standards.

## 6. Future Iteration

- Consider adding a high-level convenience function, such as `is_textual_content(content: bytes, location: Location) -> bool`, which would internally use the other detection functions to provide a simple boolean result.
