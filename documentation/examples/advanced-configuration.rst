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
Advanced Configuration
*******************************************************************************

This section demonstrates advanced usage including custom behaviors, confidence
thresholds, HTTP Content-Type parsing, and comprehensive error handling.

Custom Behaviors
===============================================================================

Confidence Thresholds
-------------------------------------------------------------------------------

Control detection confidence requirements through custom behaviors:

.. doctest:: AdvancedConfiguration

    >>> import detextive
    >>> from detextive import Behaviors

Create custom behavior configuration with confidence-related parameters:

.. doctest:: AdvancedConfiguration

    >>> strict_behaviors = Behaviors(
    ...     bytes_quantity_confidence_divisor = 512,
    ...     trial_decode_confidence = 0.9 )
    >>> content = b'Hello, world!' * 50

Use custom behaviors for detection:

.. doctest:: AdvancedConfiguration

    >>> result = detextive.detect_charset_confidence(
    ...     content,
    ...     behaviors = strict_behaviors )
    >>> result.confidence > 0.8
    True
    >>> result.charset
    'utf-8'

Trial Decode Configuration
-------------------------------------------------------------------------------

Configure how trial decoding validates detected charsets:

.. doctest:: AdvancedConfiguration

    >>> from detextive import BehaviorTristate

Always perform trial decodes for validation. The `bytes_quantity_confidence_divisor` parameter affects confidence scoring for detection:

.. doctest:: AdvancedConfiguration

    >>> validation_behaviors = Behaviors(
    ...     trial_decode = BehaviorTristate.Always,
    ...     bytes_quantity_confidence_divisor = 256 )
    >>> content = b'Content to validate through decoding'

Detect charset with validation through trial decoding:

.. doctest:: AdvancedConfiguration

    >>> charset = detextive.detect_charset(
    ...     content,
    ...     behaviors = validation_behaviors )
    >>> charset
    'utf-8'

HTTP Content-Type Parsing
===============================================================================

Content-Type Header Processing
-------------------------------------------------------------------------------

Parse HTTP Content-Type headers to extract MIME type and charset:

.. doctest:: AdvancedConfiguration

    >>> content_type = "application/json; charset=utf-8"
    >>> mimetype, charset = detextive.parse_http_content_type( content_type )
    >>> mimetype
    'application/json'
    >>> charset
    'utf-8'

Content-Type headers without charset return absent for charset:

.. doctest:: AdvancedConfiguration

    >>> mimetype, charset = detextive.parse_http_content_type( "application/json" )
    >>> mimetype
    'application/json'
    >>> type( charset ).__name__
    'AbsentSingleton'

Integration with Detection
-------------------------------------------------------------------------------

Use parsed Content-Type information to guide detection:

.. doctest:: AdvancedConfiguration

    >>> content = b'{"message": "Hello"}'
    >>> http_header = "application/json; charset=utf-8"

Let HTTP header inform detection:

.. doctest:: AdvancedConfiguration

    >>> mimetype, charset = detextive.infer_mimetype_charset(
    ...     content,
    ...     http_content_type = http_header )
    >>> mimetype
    'application/json'
    >>> charset
    'utf-8-sig'

Location-Based Inference
===============================================================================

Enhanced Context Awareness
-------------------------------------------------------------------------------

Provide rich location context to improve detection accuracy. Paths are primarily used as a fallback for MIME type detection (via file extension) and for richer exception reporting:

.. doctest:: AdvancedConfiguration

    >>> from pathlib import Path
    >>> content = b'{"key": "value", "other": "data"}'

Use Path objects for precise location context:

.. doctest:: AdvancedConfiguration

    >>> location = Path( 'document.json' )
    >>> mimetype = detextive.detect_mimetype( content, location = location )
    >>> mimetype in ('application/json', 'text/plain')  # text/plain on Windows with python-magic-bin
    True

Default Value Handling
-------------------------------------------------------------------------------

Specify fallback values when detection confidence is insufficient:

.. code-block:: python

    ambiguous_content = b'some text'

    mimetype, charset = detextive.infer_mimetype_charset(
        ambiguous_content,
        mimetype_supplement = 'text/plain',
        charset_supplement = 'utf-8' )

    print( f"Result (with defaults): {mimetype}, {charset}" )
    # Output: Result (with defaults): text/plain, utf-8

Text Validation Profiles
===============================================================================

Validation Profile Selection
-------------------------------------------------------------------------------

Choose validation strictness based on your use case:

.. doctest:: AdvancedConfiguration

    >>> text = "Sample text with ASCII characters"
    >>> text_with_unicode = "Unicode: \u2606"

Different validation profiles have varying strictness levels:

.. doctest:: AdvancedConfiguration

    >>> detextive.is_valid_text( text, profile = detextive.PROFILE_TEXTUAL )
    True
    >>> detextive.is_valid_text( text, profile = detextive.PROFILE_TERMINAL_SAFE )
    True
    >>> detextive.is_valid_text( text_with_unicode, profile = detextive.PROFILE_TEXTUAL )
    True

Profile-Aware Decoding
-------------------------------------------------------------------------------

Apply validation profiles during high-level decoding:

.. doctest:: AdvancedConfiguration

    >>> content = b'Text for terminal display'
    >>> text = detextive.decode(
    ...     content,
    ...     profile = detextive.PROFILE_TERMINAL_SAFE )
    >>> text
    'Text for terminal display'

Validation filtering can exhaust all decode attempts and raise a decode error.
Note that we provide ``http_content_type`` here to bypass MIME type detection,
which would reject this content as binary before decoding runs:

.. doctest:: AdvancedConfiguration

    >>> import detextive.exceptions
    >>> problematic = b'Text with\x00null bytes'
    >>> try:
    ...     detextive.decode(
    ...         problematic,
    ...         profile = detextive.PROFILE_TERMINAL_SAFE,
    ...         http_content_type = 'text/plain' )
    ... except detextive.exceptions.ContentDecodeFailure as exception:
    ...     print( "Decode failed after validation filtering" )
    Decode failed after validation filtering

Error Handling
===============================================================================

Exception Hierarchy
-------------------------------------------------------------------------------

Handle specific error conditions with appropriate exception types:

.. code-block:: python

    import detextive
    from detextive.exceptions import (
        CharsetDetectFailure,
        TextInvalidity,
        ContentDecodeFailure )

Attempt high-level processing with comprehensive error handling:

.. code-block:: python

    try:
        text = detextive.decode( malformed_content, location = 'data.txt' )
    except CharsetDetectFailure as exception:
        print( f"Charset detection failed: {exception}" )
    except TextInvalidity as exception:
        print( f"Text validation failed: {exception}" )
    except ContentDecodeFailure as exception:
        print( f"Decoding failed: {exception}" )
    except detextive.exceptions.Omnierror as exception:
        print( f"General detextive error: {exception}" )

Integration Patterns
===============================================================================

Complete Processing Pipeline
-------------------------------------------------------------------------------

Combine multiple detection steps in a robust processing pipeline:

.. code-block:: python

    import detextive
    from detextive import Behaviors, BehaviorTristate

    def process_document( content, location = None, http_content_type = None ):
        ''' Processes document with comprehensive detection and validation. '''
        behaviors = Behaviors(
            charset_confidence_minimum = 75,
            trial_decode = BehaviorTristate.AsNeeded )
        try:
            mimetype, charset = detextive.infer_mimetype_charset(
                content,
                behaviors = behaviors,
                location = location,
                http_content_type = http_content_type )
            if not detextive.is_textual_mimetype( mimetype ):
                return None, f"Non-textual content: {mimetype}"
            text = detextive.decode(
                content,
                behaviors = behaviors,
                profile = detextive.PROFILE_TEXTUAL,
                location = location,
                http_content_type = http_content_type )
            return text, None
        except detextive.exceptions.Omnierror as exception:
            return None, f"Processing failed: {exception}"

Example usage:

.. code-block:: python

    content = b'{"message": "Hello, world!"}'
    text, error = process_document( content, location = 'data.json' )
    if text:
        print( f"Processed text: {text}" )
    else:
        print( f"Processing error: {error}" )
