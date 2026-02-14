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
Basic Usage
*******************************************************************************

This section demonstrates core text detection capabilities. Examples progress
from simple detection to combined inference and high-level text processing.

Character Encoding Detection
===============================================================================

Basic Encoding Detection
-------------------------------------------------------------------------------

Detect character encoding from byte content:

.. doctest:: BasicUsage

    >>> import detextive
    >>> content = b'Hello, world!'
    >>> charset = detextive.detect_charset( content )
    >>> charset
    'utf-8'

UTF-8 content with special characters:

.. doctest:: BasicUsage

    >>> content = b'Caf\xc3\xa9 \xe2\x98\x85'
    >>> charset = detextive.detect_charset( content )
    >>> charset
    'utf-8'

Non-ASCII encodings can be detected with sufficient content:

.. doctest:: BasicUsage

    >>> content = 'Café Restaurant Menu\nEntrées: Soupe, Salade'.encode( 'iso-8859-1' )
    >>> charset = detextive.detect_charset( content )
    >>> charset
    'iso8859-9'

MIME Type Detection
===============================================================================

Content-Based Detection
-------------------------------------------------------------------------------

Detect MIME types from file content using magic bytes:

.. doctest:: BasicUsage

    >>> import detextive
    >>> json_content = b'{"name": "example", "value": 42}'
    >>> mimetype = detextive.detect_mimetype( json_content )
    >>> mimetype in ('application/json', 'text/plain')  # text/plain on Windows with python-magic-bin
    True

Location-aware detection combines content analysis with file extension:

.. code-block:: python

    # For plain text without magic bytes, location helps determine MIME type
    text_content = b'Plain text content'
    try:
        mimetype = detextive.detect_mimetype( text_content, location = 'document.txt' )
        print( f"Text file MIME type: {mimetype}" )
    except detextive.exceptions.MimetypeDetectFailure:
        print( "Could not detect MIME type - need more distinctive content" )
    # Note: Plain text without magic bytes may require charset detection

Binary content is correctly identified:

.. doctest:: BasicUsage

    >>> pdf_header = b'%PDF-1.4'
    >>> mimetype = detextive.detect_mimetype( pdf_header )
    >>> mimetype
    'application/pdf'

Combined Inference
===============================================================================

MIME Type and Charset Together
-------------------------------------------------------------------------------

For best accuracy, detect both MIME type and charset simultaneously:

.. doctest:: BasicUsage

    >>> import detextive
    >>> content = b'{"message": "Hello"}'
    >>> mimetype, charset = detextive.infer_mimetype_charset( content, location = 'data.json' )
    >>> mimetype
    'application/json'
    >>> charset
    'utf-8'

Plain text files with location context:

.. doctest:: BasicUsage

    >>> content = b'Sample document content'
    >>> mimetype, charset = detextive.infer_mimetype_charset( content, location = 'readme.txt' )
    >>> mimetype
    'text/plain'
    >>> charset
    'utf-8'

Confidence-Based Detection
-------------------------------------------------------------------------------

Access confidence scores for detection decisions using the confidence API:

.. doctest:: BasicUsage

    >>> import detextive
    >>> content = b'{"name": "example", "data": "test"}'
    >>> mimetype_result, charset_result = detextive.infer_mimetype_charset_confidence( content, location = 'config.json' )
    >>> mimetype_result.mimetype
    'application/json'
    >>> mimetype_result.confidence > 0.8
    True
    >>> charset_result.charset
    'utf-8'
    >>> charset_result.confidence > 0.8
    True

The confidence API is useful for quality assessment and decision making:

.. doctest:: BasicUsage

    >>> text_content = b'Plain text without magic bytes'
    >>> mimetype_result, charset_result = detextive.infer_mimetype_charset_confidence( text_content, location = 'notes.txt' )
    >>> mimetype_result.mimetype
    'text/plain'
    >>> mimetype_result.confidence > 0.7
    True

High-Level Decoding
===============================================================================

Automatic Text Decoding
-------------------------------------------------------------------------------

The ``decode`` function provides complete bytes-to-text processing:

.. doctest:: BasicUsage

    >>> import detextive
    >>> content = b'Hello, world!'
    >>> text = detextive.decode( content )
    >>> text
    'Hello, world!'

UTF-8 content is properly decoded:

.. doctest:: BasicUsage

    >>> content = b'Caf\xc3\xa9 \xe2\x98\x85'
    >>> text = detextive.decode( content )
    >>> text
    'Café ★'

Location context improves decoding decisions:

.. doctest:: BasicUsage

    >>> content = b'Sample content for analysis'
    >>> text = detextive.decode( content, location = 'document.txt' )
    >>> text
    'Sample content for analysis'

Combined Decode and Metadata
-------------------------------------------------------------------------------

The ``decode_inform`` function returns decoded text with charset/MIME metadata:

.. doctest:: BasicUsage

    >>> import detextive
    >>> result = detextive.decode_inform( b'Hello, world!\n', location = 'notes.txt' )
    >>> result.text
    'Hello, world!\n'
    >>> result.mimetype.mimetype
    'text/plain'
    >>> result.charset.charset
    'utf-8-sig'
    >>> result.linesep
    <LineSeparators.LF: '\n'>

HTTP header context is honored when textual:

.. doctest:: BasicUsage

    >>> result = detextive.decode_inform(
    ...     b'{"message":"ok"}',
    ...     http_content_type = 'application/json; charset=utf-8' )
    >>> result.mimetype.mimetype
    'application/json'

Content Validation
===============================================================================

MIME Type Classification
-------------------------------------------------------------------------------

Check if MIME types represent textual content:

.. doctest:: BasicUsage

    >>> import detextive
    >>> detextive.is_textual_mimetype( 'text/plain' )
    True
    >>> detextive.is_textual_mimetype( 'application/json' )
    True
    >>> detextive.is_textual_mimetype( 'image/jpeg' )
    False

Text Quality Validation
-------------------------------------------------------------------------------

Validate that decoded text meets quality standards:

.. doctest:: BasicUsage

    >>> import detextive
    >>> text = "Hello, world!"
    >>> detextive.is_valid_text( text )
    True

Text with control characters fails validation:

.. doctest:: BasicUsage

    >>> text_with_controls = "Hello\x00\x01world"
    >>> detextive.is_valid_text( text_with_controls )
    False

Different types of text content and their validation:

.. doctest:: BasicUsage

    >>> detextive.is_valid_text( "Hello, world!" )
    True
    >>> detextive.is_valid_text( "Hello\x00\x01world" )
    False
    >>> detextive.is_valid_text( "   \n\t  " )
    True
    >>> detextive.is_valid_text( "" )
    True
