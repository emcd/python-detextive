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
Line Separator Processing
*******************************************************************************

This section demonstrates cross-platform line ending detection and 
normalization. Examples cover mixed content handling and platform-specific 
conversions.

Line Separator Detection
===============================================================================

Detecting Line Endings in Bytes
-------------------------------------------------------------------------------

Detect the predominant line separator in byte content:

.. doctest:: LineSeparators

    >>> import detextive
    >>> from detextive import LineSeparators
    
    >>> unix_content = b'Line 1\nLine 2\nLine 3'
    >>> separator = LineSeparators.detect_bytes( unix_content )
    >>> separator
    <LineSeparators.LF: '\n'>

Windows-style line endings:

.. doctest:: LineSeparators

    >>> windows_content = b'Line 1\r\nLine 2\r\nLine 3'
    >>> separator = LineSeparators.detect_bytes( windows_content )
    >>> separator
    <LineSeparators.CRLF: '\r\n'>

Detecting Line Endings in Text
-------------------------------------------------------------------------------

Detection also works with text strings:

.. doctest:: LineSeparators

    >>> mixed_content = 'Line 1\r\nLine 2\rLine 3\n'
    >>> separator = LineSeparators.detect_text( mixed_content )
    >>> separator
    <LineSeparators.CRLF: '\r\n'>

When line endings are mixed, the first detected type is returned:

.. doctest:: LineSeparators

    >>> mixed_unix_first = 'A\nB\nC\nD\r\nE'
    >>> separator = LineSeparators.detect_text( mixed_unix_first )
    >>> separator
    <LineSeparators.LF: '\n'>

Line Ending Normalization
===============================================================================

Universal Normalization
-------------------------------------------------------------------------------

Normalize any line endings to Python's standard (LF):

.. doctest:: LineSeparators

    >>> mixed_content = 'Line 1\r\nLine 2\rLine 3\n'
    >>> normalized = LineSeparators.normalize_universal( mixed_content )
    >>> normalized
    'Line 1\nLine 2\nLine 3\n'

The normalization handles all three line ending types:

.. doctest:: LineSeparators

    >>> complex_content = 'Unix\nWindows\r\nMac\rMixed'
    >>> normalized = LineSeparators.normalize_universal( complex_content )
    >>> normalized
    'Unix\nWindows\nMac\nMixed'

Platform-Specific Conversion
-------------------------------------------------------------------------------

Convert normalized text to specific line ending formats:

.. doctest:: LineSeparators

    >>> normalized = 'Line 1\nLine 2\nLine 3'
    >>> windows_format = LineSeparators.CRLF.nativize( normalized )
    >>> windows_format
    'Line 1\r\nLine 2\r\nLine 3'

Unix format (no change needed):

.. doctest:: LineSeparators

    >>> unix_format = LineSeparators.LF.nativize( normalized )
    >>> unix_format
    'Line 1\nLine 2\nLine 3'

Complete Processing Workflow
===============================================================================

Detection and Normalization Pipeline
-------------------------------------------------------------------------------

A typical workflow for handling text with unknown line endings:

.. doctest:: LineSeparators

    >>> import detextive
    >>> from detextive import LineSeparators
    
    >>> # Content with mixed line endings
    >>> raw_content = 'Header\r\nUnix line\nMac line\rFooter'
    
    >>> # Detect the predominant line ending
    >>> detected = LineSeparators.detect_text( raw_content )
    >>> print( f"Detected line ending: {detected.name}" )
    Detected line ending: CRLF
    
    >>> # Normalize to Python standard
    >>> normalized = LineSeparators.normalize_universal( raw_content )
    >>> print( f"Normalized: {repr( normalized )}" )
    Normalized: 'Header\nUnix line\nMac line\nFooter'
    
    >>> # Convert to target platform
    >>> target_format = LineSeparators.CRLF.nativize( normalized )
    >>> print( f"Target format: {repr( target_format )}" )
    Target format: 'Header\r\nUnix line\r\nMac line\r\nFooter'

Processing Binary Content
-------------------------------------------------------------------------------

Handle line endings in binary data before text processing:

.. doctest:: LineSeparators

    >>> import detextive
    >>> from detextive import LineSeparators
    
    >>> # Binary content with mixed line endings
    >>> binary_content = b'Data\r\nMore data\nFinal data\r'
    
    >>> # Detect line separator
    >>> separator = LineSeparators.detect_bytes( binary_content )
    >>> print( f"Binary line ending: {separator.name}" )
    Binary line ending: CRLF
    
    >>> # Convert to text for normalization
    >>> text_content = binary_content.decode( 'utf-8' )
    >>> normalized = LineSeparators.normalize_universal( text_content )
    >>> print( f"Normalized text: {repr( normalized )}" )
    Normalized text: 'Data\nMore data\nFinal data\n'

Edge Cases and Special Handling
===============================================================================

Empty and Single-Line Content
-------------------------------------------------------------------------------

Line separator detection handles edge cases gracefully:

.. doctest:: LineSeparators

    >>> # Empty content
    >>> empty_separator = LineSeparators.detect_text( '' )
    >>> empty_separator is None
    True

    >>> # Single line without ending
    >>> single_line = 'Just one line'
    >>> single_separator = LineSeparators.detect_text( single_line )
    >>> single_separator is None
    True

