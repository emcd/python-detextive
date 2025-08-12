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
Text Processing Examples
*******************************************************************************

This section demonstrates practical usage of core text processing capabilities.
Examples progress from basic usage to more advanced scenarios including error
handling and edge cases.

Character Encoding Detection
===============================================================================

Basic Encoding Detection
-------------------------------------------------------------------------------

Detect character encoding from byte content:

.. doctest:: Detection

    >>> import detextive
    >>> content = b'Hello, world!'
    >>> encoding = detextive.detect_charset( content )
    >>> print( encoding )
    utf-8

UTF-8 content is correctly identified:

.. doctest:: Detection

    >>> content = b'Caf\xc3\xa9 \xe2\x98\x85'
    >>> encoding = detextive.detect_charset( content )
    >>> print( encoding )
    utf-8

Empty content returns ``None``:

.. doctest:: Detection

    >>> content = b''
    >>> encoding = detextive.detect_charset( content )
    >>> print( encoding )
    None

MIME Type Detection
===============================================================================

Content-Based Detection
-------------------------------------------------------------------------------

Detect MIME types using magic numbers and file extensions:

.. doctest:: Detection

    >>> import detextive
    >>> from pathlib import Path
    >>>
    >>> content = b'{"name": "example", "value": 42}'
    >>> mimetype = detextive.detect_mimetype( content, 'data.json' )
    >>> print( mimetype )
    application/json

JPEG image detection using magic numbers:

.. doctest:: Detection

    >>> content = b'\xff\xd8\xff\xe0\x00\x10JFIF'
    >>> mimetype = detextive.detect_mimetype( content, 'photo.jpg' )
    >>> print( mimetype )
    image/jpeg

Extension Fallback
-------------------------------------------------------------------------------

When magic number detection fails, extension-based detection is used:

.. doctest:: Detection

    >>> content = b'some content without magic numbers'
    >>> mimetype = detextive.detect_mimetype( content, 'document.pdf' )
    >>> print( mimetype )
    application/pdf

Path objects work as location parameters:

.. doctest:: Detection

    >>> from pathlib import Path
    >>> location = Path( 'document.txt' )
    >>> content = b'Plain text content for demonstration'
    >>> mimetype = detextive.detect_mimetype( content, location )
    >>> print( mimetype )
    text/plain

Combined Detection
===============================================================================

Detecting Both MIME Type and Charset
-------------------------------------------------------------------------------

Get both MIME type and character encoding in one call:

.. doctest:: Detection

    >>> content = b'<html><body>Hello World</body></html>'
    >>> mimetype, charset = detextive.detect_mimetype_and_charset( content, 'page.html' )
    >>> print( f'MIME: {mimetype}, Charset: {charset}' )
    MIME: text/html, Charset: utf-8

For content with only charset detection:

.. doctest:: Detection

    >>> content = b'Just some plain text content'
    >>> mimetype, charset = detextive.detect_mimetype_and_charset( content, 'unknown' )
    >>> print( f'MIME: {mimetype}, Charset: {charset}' )
    MIME: text/plain, Charset: utf-8

Content with unknown extension but detectable charset defaults to text/plain:

.. doctest:: Detection

    >>> content = b'readable text content without clear file type'
    >>> mimetype, charset = detextive.detect_mimetype_and_charset( content, 'unknown_file' )
    >>> print( f'MIME: {mimetype}, Charset: {charset}' )
    MIME: text/plain, Charset: utf-8

Override Parameters
-------------------------------------------------------------------------------

Override detected values using parameter overrides:

.. doctest:: Detection

    >>> content = b'<?xml version="1.0"?><root>data</root>'
    >>> mimetype, charset = detextive.detect_mimetype_and_charset(
    ...     content, 'data.xml', charset = 'iso-8859-1'
    ... )
    >>> print( f'MIME: {mimetype}, Charset: {charset}' )
    MIME: application/xml, Charset: iso-8859-1

Content Validation
===============================================================================

MIME Type Validation
-------------------------------------------------------------------------------

Check if MIME types represent textual content:

.. doctest:: Validation

    >>> import detextive
    >>>
    >>> print( detextive.is_textual_mimetype( 'text/plain' ) )
    True
    >>> print( detextive.is_textual_mimetype( 'text/html' ) )
    True

Application types with textual content:

.. doctest:: Validation

    >>> print( detextive.is_textual_mimetype( 'application/json' ) )
    True
    >>> print( detextive.is_textual_mimetype( 'application/xml' ) )
    True
    >>> print( detextive.is_textual_mimetype( 'application/javascript' ) )
    True

Textual suffixes are recognized:

.. doctest:: Validation

    >>> print( detextive.is_textual_mimetype( 'application/vnd.api+json' ) )
    True
    >>> print( detextive.is_textual_mimetype( 'application/custom+xml' ) )
    True

Non-textual types return ``False``:

.. doctest:: Validation

    >>> print( detextive.is_textual_mimetype( 'image/jpeg' ) )
    False
    >>> print( detextive.is_textual_mimetype( 'video/mp4' ) )
    False
    >>> print( detextive.is_textual_mimetype( 'application/octet-stream' ) )
    False

Edge Cases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Empty and malformed MIME types:

.. doctest:: Validation

    >>> print( detextive.is_textual_mimetype( '' ) )
    False
    >>> print( detextive.is_textual_mimetype( 'invalid' ) )
    False

Text Reasonableness Testing
-------------------------------------------------------------------------------

Validate that byte content represents textual data:

.. doctest:: Validation

    >>> import detextive
    >>>
    >>> content = b'This is readable text with proper formatting.'
    >>> print( detextive.is_textual_content( content ) )
    True

Content with acceptable whitespace:

.. doctest:: Validation

    >>> content = b'Line 1\n\tIndented line\nLast line'
    >>> print( detextive.is_textual_content( content ) )
    True

Rejecting Non-Textual Content
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Empty content is rejected:

.. doctest:: Validation

    >>> print( detextive.is_textual_content( b'' ) )
    False

Non-textual content is rejected:

.. doctest:: Validation

    >>> content = b'\x00\x01\x02\x03\x04\x05'
    >>> print( detextive.is_textual_content( content ) )
    False

Line Separator Detection
===============================================================================

Detecting Line Endings
-------------------------------------------------------------------------------

Detect line separators from byte content:

.. doctest:: Detection

    >>> import detextive
    >>>
    >>> content = b'line1\nline2\nline3'
    >>> separator = detextive.LineSeparators.detect_bytes( content )
    >>> print( separator )
    LineSeparators.LF

Windows line endings:

.. doctest:: Detection

    >>> content = b'line1\r\nline2\r\nline3'
    >>> separator = detextive.LineSeparators.detect_bytes( content )
    >>> print( separator )
    LineSeparators.CRLF

No line separators found:

.. doctest:: Detection

    >>> content = b'just one line'
    >>> separator = detextive.LineSeparators.detect_bytes( content )
    >>> print( separator )
    None

Line Ending Normalization
===============================================================================

Universal Normalization
-------------------------------------------------------------------------------

Convert all line endings to Unix format:

.. doctest:: Conversion

    >>> import detextive
    >>> content = 'Line 1\r\nLine 2\rLine 3\nLine 4'
    >>> normalized = detextive.LineSeparators.normalize_universal( content )
    >>> print( repr( normalized ) )
    'Line 1\nLine 2\nLine 3\nLine 4'

Specific Line Ending Conversion
-------------------------------------------------------------------------------

Convert specific line endings:

.. doctest:: Conversion

    >>> content = 'First line\r\nSecond line'
    >>> result = detextive.LineSeparators.CRLF.normalize( content )
    >>> print( repr( result ) )
    'First line\nSecond line'

Convert Unix endings to platform-specific:

.. doctest:: Conversion

    >>> content = 'First line\nSecond line'
    >>> result = detextive.LineSeparators.CRLF.nativize( content )
    >>> print( repr( result ) )
    'First line\r\nSecond line'

Error Handling
===============================================================================

Exception Scenarios
-------------------------------------------------------------------------------

The exception hierarchy follows standard patterns. Exception classes are
available for handling error conditions:

.. doctest:: Detection

    >>> import detextive
    >>> from detextive import exceptions
    >>>
    >>> print( hasattr( exceptions, 'TextualMimetypeInvalidity' ) )
    True

The exception hierarchy follows standard patterns:

.. doctest:: Detection

    >>> print( issubclass( exceptions.TextualMimetypeInvalidity, exceptions.Omnierror ) )
    True
    >>> print( issubclass( exceptions.Omnierror, exceptions.Omniexception ) )
    True
