.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+


*******************************************************************************
Core Functionality Test Plan
*******************************************************************************

Test Plan: detection.py and lineseparators.py

Coverage Analysis Summary
===============================================================================

detection.py
-------------------------------------------------------------------------------

- Current coverage: 77%
- Target coverage: 95%+ (focused on critical paths)
- Remaining uncovered lines: 77-81, 111, 121, 124-128, 173-174, 176
- Critical gaps: ASCII charset fallback, parameter overrides, exception paths

lineseparators.py
-------------------------------------------------------------------------------

- Current coverage: 91%
- Target coverage: 95%+ (focused on critical paths)  
- Remaining uncovered branches: 4 exit conditions in enum methods
- Status: Good coverage, mainly missing edge case branches

Focused Test Cases for Remaining Coverage Gaps
===============================================================================

Priority Test Cases to Close Critical Coverage Gaps
-------------------------------------------------------------------------------

**ASCII Charset Detection (Lines 77-81)**

- Test content that chardet detects as 'ascii' → should return 'utf-8'
- Test content that chardet detects as 'MacRoman' but decodes as UTF-8 → should return 'utf-8'
- Test content that chardet detects as 'iso-8859-1' and fails UTF-8 decode → should return 'iso-8859-1'

**Parameter Override Cases (Line 111)**

- Test ``detect_mimetype_and_charset()`` with explicit mimetype override
- Test with both mimetype and charset overrides

**Fallback to Octet-Stream (Line 121)** 

- Test with binary content that has no detectable mimetype or charset

**Exception Path Testing (Lines 124-128, 173-174, 176)**

- Test non-textual mimetype (e.g., 'image/jpeg') with detected charset but no reasonable text content
- Test invalid charset name (LookupError) in validation
- Test content that can't be decoded with detected charset (UnicodeDecodeError)
- Test decoded content that fails reasonableness checks

**Exception Constructor Coverage (exceptions.py Lines 43, 52, 61)**

- Raise each exception type to test constructor message formatting

Test Strategy
===============================================================================

detection.py Component-Specific Tests
-------------------------------------------------------------------------------

Function: detect_charset (Tests 100-199)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Happy path**: Valid text content with various encodings (UTF-8, ASCII, latin-1, cp1252)
- **UTF-8 bias logic**: Content that could be multiple encodings but should return UTF-8
- **ASCII superset handling**: ASCII content should return 'utf-8'
- **chardet failure**: Content where chardet returns None
- **False positive elimination**: Content detected as MacRoman but actually UTF-8
- **Edge cases**: Empty content, binary content, mixed encoding markers

Function: detect_mimetype (Tests 200-299)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Content-based detection**: Files with clear magic numbers (JPEG, PNG, PDF)
- **Extension fallback**: Files without magic numbers falling back to mimetypes.guess_type
- **PureError handling**: Content that triggers puremagic.PureError
- **ValueError handling**: Malformed content triggering ValueError
- **Location parameter variations**: str and Path inputs

Function: detect_mimetype_and_charset (Tests 300-399)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Both detected**: Content with both clear mimetype and charset
- **Mimetype override**: Using absential parameter to override detection
- **Charset override**: Using absential parameter to override detection
- **Text/plain fallback**: Charset detected but no mimetype
- **Octet-stream fallback**: Neither detected
- **TextualMimetypeInvalidity cases**: Non-textual mimetype with charset but validation fails
- **Validation success**: Non-textual mimetype with valid charset and reasonable content

Function: is_textual_mimetype (Tests 400-499)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **text/* prefix**: text/plain, text/html, text/x-custom
- **Specific application types**: All types in _TEXTUAL_MIME_TYPES frozenset
- **Textual suffixes**: Custom types with +xml, +json, +yaml, +toml suffixes
- **Non-textual types**: image/jpeg, video/mp4, application/octet-stream
- **Edge cases**: Empty string, malformed MIME types like "text" or "text//html"

Function: is_reasonable_text_content (Tests 500-599)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Valid text content**: Normal readable text with proper character distribution
- **Empty content rejection**: Empty strings should return False
- **Control character limits**: Content with >10% control characters (excluding \\t\\n\\r)
- **Printable character ratio**: Content with <80% printable characters
- **Common whitespace handling**: Content with tabs, newlines, carriage returns
- **Binary-like content**: Content that appears to be binary data

Function: _validate_mimetype_with_trial_decode (Tests 600-699)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Successful decode and validation**: Valid charset and reasonable text content
- **UnicodeDecodeError**: Invalid charset for the content
- **LookupError**: Unknown/invalid charset name
- **Unreasonable content**: Valid decode but content fails reasonableness test
- **Exception chaining**: Verify TextualMimetypeInvalidity is raised with proper cause

lineseparators.py Component-Specific Tests
-------------------------------------------------------------------------------

LineSeparators Enum Basic Tests (Tests 100-199)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Enum members**: CR, CRLF, LF values and string representations
- **Enum behavior**: Comparison, hashing, iteration

Method: LineSeparators.detect_bytes (Tests 200-299)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **LF detection**: Unix-style \\n line endings
- **CRLF detection**: Windows-style \\r\\n line endings
- **CR detection**: Classic Mac \\r line endings
- **Mixed content**: Content with multiple line ending types (first wins)
- **No line endings**: Content without any line separators
- **Limit parameter**: Content longer than limit with line endings beyond limit
- **Edge cases**: Empty content, single character content
- **Byte vs int sequence**: Both bytes objects and Sequence[int] inputs

Method: LineSeparators.normalize_universal (Tests 300-399)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **CRLF to LF**: Windows line endings converted to Unix
- **CR to LF**: Classic Mac line endings converted to Unix
- **Mixed line endings**: Content with both CRLF and CR converted
- **Already LF**: Unix content unchanged
- **No line endings**: Content without line separators unchanged
- **Edge cases**: Empty string, single line ending character

Method: LineSeparators.normalize (Tests 400-499)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **CR instance normalization**: CR enum member converting \\r to \\n
- **CRLF instance normalization**: CRLF enum member converting \\r\\n to \\n
- **LF instance normalization**: LF enum member should return unchanged
- **Multiple occurrences**: Content with multiple instances of the separator
- **No matching separators**: Content without the specific separator

Method: LineSeparators.nativize (Tests 500-599)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **CR instance nativization**: Converting \\n to \\r
- **CRLF instance nativization**: Converting \\n to \\r\\n
- **LF instance nativization**: LF enum member should return unchanged
- **Multiple line endings**: Content with multiple \\n converted appropriately
- **No line endings**: Content without \\n unchanged

Implementation Notes
===============================================================================

Dependencies requiring injection: None
-------------------------------------------------------------------------------

- All functions are pure with standard library dependencies
- chardet, puremagic, mimetypes can be mocked if needed but may not be necessary

Filesystem operations needing pyfakefs: None
-------------------------------------------------------------------------------

- Functions operate on in-memory content, no file I/O required

External services requiring mocking: None
-------------------------------------------------------------------------------

- No external network calls or services

Test data strategy
-------------------------------------------------------------------------------

- **Primary approach**: Inline byte arrays in test code (100% of tests)

  - ``b"Hello \\xc3\\xa9 world"`` for UTF-8 content
  - ``b"Simple ASCII text"`` for ASCII content  
  - ``b"Line 1\\r\\nLine 2\\r\\nLine 3"`` for line ending tests
  - ``b'\\xff\\xd8\\xff\\xe0\\x00\\x10JFIF'`` for JPEG magic number testing

- **No file fixtures needed**: All test data can be represented as byte literals

Private functions/methods testable via public API
-------------------------------------------------------------------------------

- ``_validate_mimetype_with_trial_decode()`` is called by ``detect_mimetype_and_charset()``
- Test through public API by providing scenarios that trigger validation

Areas requiring immutability constraint violations: None
-------------------------------------------------------------------------------

- All code is testable through public interfaces without monkey-patching

Third-party testing patterns to research
-------------------------------------------------------------------------------

- Mock puremagic.from_string() exceptions if needed
- Mock chardet.detect() return values for edge cases
- Mock mimetypes.guess_type() for extension fallback testing

Test module numbering
-------------------------------------------------------------------------------

Current test structure:
- ``test_000_package.py`` - package sanity checks (existing)
- ``test_010_base.py`` - imports testing (existing)

Needed test modules for 100% coverage:
- ``test_100_exceptions.py`` - exception classes testing
- ``test_200_detection.py`` - detection module functional testing
- ``test_210_lineseparators.py`` - line separators enum functional testing

Anti-patterns to avoid
-------------------------------------------------------------------------------

- Testing against real external sites (not applicable)
- Monkey-patching internal code (use mocking of external deps only if needed)
- Over-mocking (prefer real function execution with varied inputs)

Success Metrics
===============================================================================

- Target line coverage: 100% for both detection.py and lineseparators.py
- Target branch coverage: 100% for both modules
- Specific gaps to close: Lines 77-81, 111, 121, 124-128, 173-174, 176 in detection.py
- Exception testing: Ensure all 3 exception classes are instantiated and tested

**100% Coverage Approach**

Since all uncovered lines are testable without complex mocking:
- Target: 100% line and branch coverage
- Estimated: 15-20 focused test cases across 3 new test modules
- Strategy: Direct testing of edge cases and error paths
- No `#pragma: no cover` needed - all code paths are legitimately testable