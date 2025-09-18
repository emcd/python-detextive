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
Test Content Patterns Specification
*******************************************************************************

Overview
===============================================================================

This document specifies a centralized test content patterns module providing
curated byte sequences for comprehensive testing without filesystem dependencies.
The patterns support systematic testing of charset detection, MIME type
detection, validation, and cross-platform compatibility scenarios.

Module Structure
===============================================================================

Location: ``tests/test_000_detextive/patterns.py``

The patterns module provides categorized byte sequences with known expected
outcomes for deterministic testing across all detection components.

Charset Detection Patterns
-------------------------------------------------------------------------------

**UTF-8 Samples**::

    UTF8_BASIC = b'Hello, world!'
    UTF8_WITH_BOM = b'\xef\xbb\xbfHello, world!'
    UTF8_EMOJI = b'Hello \xf0\x9f\x91\x8b world!'
    UTF8_MULTIBYTE = b'Caf\xc3\xa9 na\xc3\xafve r\xc3\xa9sum\xc3\xa9'
    UTF8_ACCENTED = b'\xc3\xa9\xc3\xa8\xc3\xa0\xc3\xa7'

**ASCII-Compatible Samples**::

    ASCII_BASIC = b'Simple ASCII text without special characters'
    ASCII_PRINTABLE = b'!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~'
    ASCII_WHITESPACE = b'Line 1\n\tIndented line\r\nWindows line'

**Latin-1 Samples**::

    LATIN1_BASIC = b'Caf\xe9 na\xefve r\xe9sum\xe9'  # ISO-8859-1
    LATIN1_EXTENDED = b'\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf'

**Windows-1252 Samples**::

    CP1252_QUOTES = b'\x93smart quotes\x94 and \x96dashes\x97'
    CP1252_CURRENCY = b'Price: \x80 12.99'  # Euro symbol

**Ambiguous Content**::

    AMBIGUOUS_ASCII = b'This could be any ASCII-compatible charset'
    AMBIGUOUS_LATIN = b'\xe9\xe8\xe0'  # Could be Latin-1 or CP1252

**Malformed Content**::

    INVALID_UTF8 = b'\xff\xfe\xfd'  # Invalid UTF-8 sequences
    TRUNCATED_UTF8 = b'Valid start \xc3'  # Incomplete multibyte
    MIXED_ENCODING = b'ASCII \xc3\xa9 then \xe9'  # Mixed UTF-8/Latin-1

MIME Type Detection Patterns
-------------------------------------------------------------------------------

**Text Content**::

    TEXT_PLAIN = b'This is plain text content for testing purposes.'
    TEXT_HTML = b'<html><head><title>Test</title></head><body>Content</body></html>'
    TEXT_CSS = b'body { margin: 0; padding: 0; background: #fff; }'
    TEXT_JAVASCRIPT = b'function test() { return "hello world"; }'
    TEXT_XML = b'<?xml version="1.0"?><root><element>value</element></root>'

**JSON Content**::

    JSON_SIMPLE = b'{"key": "value", "number": 42, "array": [1, 2, 3]}'
    JSON_UNICODE = b'{"message": "\u00c9\u00e9\u00e8\u00e0", "emoji": "\ud83d\udc4b"}'
    JSON_NESTED = b'{"outer": {"inner": {"deep": "value"}}, "list": [{"item": 1}]}'

**Binary Content with Magic Bytes**::

    # Image formats
    JPEG_HEADER = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
    PNG_HEADER = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    GIF_HEADER = b'GIF89a\x01\x00\x01\x00\x00\x00\x00'

    # Archive formats
    ZIP_HEADER = b'PK\x03\x04\x14\x00\x00\x00\x08\x00'
    PDF_HEADER = b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n'

    # Executable formats
    PE_HEADER = b'MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff'
    ELF_HEADER = b'\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'

**Cross-Platform Considerations**::

    # Content that python-magic vs python-magic-bin detect differently
    JSON_AMBIGUOUS = b'{"data": "value"}'  # May be application/json or text/plain
    XML_SIMPLE = b'<note><body>content</body></note>'  # May vary by platform

Line Separator Patterns
-------------------------------------------------------------------------------

**Platform-Specific Line Endings**::

    UNIX_LINES = b'line1\nline2\nline3\n'
    WINDOWS_LINES = b'line1\r\nline2\r\nline3\r\n'
    MAC_CLASSIC_LINES = b'line1\rline2\rline3\r'

**Mixed Line Endings**::

    MIXED_UNIX_WINDOWS = b'line1\nline2\r\nline3\n'
    MIXED_ALL_TYPES = b'line1\nline2\r\nline3\rline4\n'
    CONSECUTIVE_SEPARATORS = b'line1\n\nline2\r\n\r\nline3'

**Edge Cases**::

    NO_LINE_ENDINGS = b'single line without any separators'
    ONLY_SEPARATORS = b'\n\r\n\r'
    CR_NOT_CRLF = b'line1\rX\rline2'  # CR followed by non-LF

Content Length Patterns
-------------------------------------------------------------------------------

**Confidence Testing**::

    EMPTY_CONTENT = b''
    MINIMAL_CONTENT = b'a'
    SHORT_CONTENT = b'Short content for low confidence testing'
    MEDIUM_CONTENT = b'A' * 512  # Half of default confidence divisor
    LONG_CONTENT = b'A' * 1024   # Full confidence threshold
    VERY_LONG_CONTENT = b'A' * 2048  # Above confidence threshold

**Repeated Patterns**::

    REPEATED_CHAR = b'a' * 100
    REPEATED_SEQUENCE = b'abc' * 100
    REPEATED_UTF8 = b'\xc3\xa9' * 100  # Repeated é

Validation Patterns
-------------------------------------------------------------------------------

**Textual Content**::

    REASONABLE_TEXT = b'This is reasonable text with proper punctuation.'
    WHITESPACE_HEAVY = b'   \t\n\r   \t\n\r   '
    CONTROL_CHARS = b'\x01\x02\x03\x04\x05'
    MIXED_REASONABLE = b'Normal text \x09 with some \x0a control chars'

**Non-Textual Content**::

    BINARY_DATA = bytes(range(256))  # All possible byte values
    NULL_HEAVY = b'\x00' * 50
    HIGH_BYTES = bytes(range(128, 256))

Error Condition Patterns
-------------------------------------------------------------------------------

**Detection Failure Scenarios**::

    UNDETECTABLE_CHARSET = b'\x80\x81\x82\x83'  # Ambiguous bytes
    UNDETECTABLE_MIMETYPE = b'UNKN\x00\x01\x02\x03'  # No clear magic
    CONFLICTING_INDICATORS = b'{\x80\x81\x82\x83}'  # JSON-like but invalid UTF-8

**Exception Trigger Patterns**::

    DECODE_FAILURE_UTF8 = b'Valid start \xff\xfe then invalid'
    DECODE_FAILURE_LATIN1 = b'\xff\xfe\xfd'  # Invalid for most charsets except Latin-1

Location Context Patterns
-------------------------------------------------------------------------------

**File Extension Hints**::

    EXTENSIONS = {
        'text': ['.txt', '.log', '.md', '.rst'],
        'code': ['.py', '.js', '.css', '.html', '.xml'],
        'data': ['.json', '.csv', '.yaml', '.toml'],
        'binary': ['.jpg', '.png', '.pdf', '.zip', '.exe'],
        'ambiguous': ['.bin', '.dat', '.tmp', ''],
    }

**URL Context Patterns**::

    URLS = [
        'http://example.com/document.txt',
        'https://api.example.com/data.json',
        'file:///path/to/local/file.py',
        '/absolute/path/file.log',
        'relative/path/file.md',
    ]

Windows Compatibility Patterns
-------------------------------------------------------------------------------

**Python-Magic vs Python-Magic-Bin Differences**::

    # Content that detects differently on Windows vs Unix
    JSON_PLATFORM_VARIANT = b'{"test": "data"}'
    # Expected: application/json (Unix) vs text/plain (Windows)

    XML_PLATFORM_VARIANT = b'<test>data</test>'
    # Expected: application/xml (Unix) vs text/xml (Windows)

**Cygwin-Specific Considerations**::

    LARGE_CONTENT = b'A' * 10000  # Test buffer handling
    UNICODE_HEAVY = 'Test with unicode: ' + '🌟' * 100
    UNICODE_HEAVY_BYTES = UNICODE_HEAVY.encode('utf-8')

Pattern Metadata
===============================================================================

Each pattern includes metadata for expected outcomes::

    PATTERN_METADATA = {
        'UTF8_BASIC': {
            'expected_charset': 'utf-8',
            'expected_mimetype': 'text/plain',
            'confidence_minimum': 0.8,
            'is_textual': True,
            'line_separator': None,
        },
        'JPEG_HEADER': {
            'expected_charset': None,
            'expected_mimetype': 'image/jpeg',
            'confidence_minimum': 0.9,
            'is_textual': False,
            'line_separator': None,
        },
        # ... Additional metadata for all patterns
    }

Usage Guidelines
===============================================================================

**Test Pattern Selection**::

    # Import patterns in test modules
    from .patterns import UTF8_BASIC, JPEG_HEADER, PATTERN_METADATA

    # Use with expected outcomes
    def test_charset_detection():
        result = detect_charset(UTF8_BASIC)
        expected = PATTERN_METADATA['UTF8_BASIC']['expected_charset']
        assert result == expected

**Cross-Platform Testing**::

    # Use platform variants for Windows compatibility
    def test_json_detection_cross_platform():
        result = detect_mimetype(JSON_PLATFORM_VARIANT)
        # Accept either Unix or Windows detection
        assert result in ['application/json', 'text/plain']

**Property-Based Testing Integration**::

    # Combine with hypothesis for edge case generation
    @given(content=st.sampled_from([UTF8_BASIC, LATIN1_BASIC, ASCII_BASIC]))
    def test_charset_detection_deterministic(content):
        result1 = detect_charset(content)
        result2 = detect_charset(content)
        assert result1 == result2

Implementation Notes
===============================================================================

- All patterns are defined as module-level byte constants
- Metadata dictionary provides expected outcomes for assertions
- Patterns cover both positive cases (successful detection) and negative cases (detection failures)
- Cross-platform variants account for python-magic vs python-magic-bin differences
- Content length patterns enable confidence scoring validation
- Location patterns support context-aware detection testing