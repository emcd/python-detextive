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
001. Python API Design Specification
*******************************************************************************

Overview
===============================================================================

This document specifies the Python API design for the detextive library's
initial feature set, implementing faithful functional reproduction of existing
text detection capabilities from mimeogram, cache proxy, and ai-experiments
packages.

The design prioritizes behavioral fidelity and minimal migration effort while
following established project practices for interface contracts, module
organization, and naming conventions.

Public Interface Specification
===============================================================================

Core Detection Functions
-------------------------------------------------------------------------------

**Character Encoding Detection**

.. code-block:: python

    def detect_charset( content: bytes ) -> __.typx.Optional[ str ]:
        ''' Detects character encoding with UTF-8 preference and validation.
        
            Applies statistical analysis using chardet library with UTF-8 bias.
            Validates detected encodings through trial decoding to eliminate
            false positives like 'MacRoman'. Returns encoding names compatible 
            with Python's codec system.
            
            Returns None if no reliable encoding can be determined.
        '''

**MIME Type Detection**

.. code-block:: python

    def detect_mimetype(
        content: bytes,
        location: __.cabc.Sequence[ str ] | __.Path | str
    ) -> __.typx.Optional[ str ]:
        ''' Detects MIME type using content analysis and extension fallback.
            
            Returns standardized MIME type strings or None if detection fails.
        '''

**Combined Detection with Parameter Overrides**

.. code-block:: python

    def detect_mimetype_and_charset(
        content: bytes,
        location: __.cabc.Sequence[ str ] | __.Path | str, *,
        mimetype: __.Absential[ str ] = __.absent,
        charset: __.Absential[ str ] = __.absent,
    ) -> tuple[ str, __.typx.Optional[ str ] ]:
        ''' Detects MIME type and charset with optional parameter overrides.
            
            Returns tuple of (mimetype, charset). MIME type defaults to 
            'text/plain' if charset detected but MIME type unknown, or 
            'application/octet-stream' if neither detected.
        '''

**Textual Content Validation**

.. code-block:: python

    def is_textual_mimetype( mimetype: str ) -> bool:
        ''' Validates if MIME type represents textual content.
        
            Consolidates textual MIME type patterns from all source 
            implementations. Supports text/* prefix, specific application
            types (JSON, XML, JavaScript, etc.), and textual suffixes
            (+xml, +json, +yaml, +toml).
            
            Returns True for MIME types representing textual content.
        '''

    def is_reasonable_text_content( content: str ) -> bool:
        ''' Validates decoded content using heuristic analysis.
        
            Applies heuristics to detect meaningful text vs binary data:
            - Rejects empty content and single-character repetition
            - Limits control characters to <10% (excluding common whitespace)
            - Requires >=80% printable characters
            
            Returns True for content likely to be meaningful text.
        '''

Line Separator Processing
-------------------------------------------------------------------------------

**LineSeparators Enum**

.. code-block:: python

    class LineSeparators( __.enum.Enum ):
        ''' Line separators for cross-platform text processing. '''
        
        CR = '\r'     # Classic MacOS (0xD)
        CRLF = '\r\n' # DOS/Windows (0xD 0xA)
        LF = '\n'     # Unix/Linux (0xA)
        
        @classmethod
        def detect_bytes(
            selfclass,
            content: __.cabc.Sequence[ int ] | bytes,
            limit: int = 1024
        ) -> __.typx.Optional[ 'LineSeparators' ]:
            ''' Detects line separator from byte content sample.
            
                Returns detected LineSeparators enum member or None.
            '''
        
        @classmethod
        def normalize_universal( selfclass, content: str ) -> str:
            ''' Normalizes all line separators to Unix LF format.
            '''
        
        def normalize( self, content: str ) -> str:
            ''' Normalizes specific line separator to Unix LF format.
            '''
        
        def nativize( self, content: str ) -> str:
            ''' Converts Unix LF to this platform's line separator.
            '''

Interface Contract Principles
===============================================================================

Wide Parameters, Narrow Returns
-------------------------------------------------------------------------------

**Parameter Design:**
- Accept abstract base classes for maximum flexibility
- Support multiple input formats (bytes, Path, str, Sequence[str])
- Use Union types for naturally variable inputs

**Return Design:**
- Return concrete, immutable types (str, tuple, enum members)
- Prefer specific types over generic containers
- Use None for explicit "not detected" semantics

**Examples:**

.. code-block:: python

    # Wide parameters: accept any sequence-like or path-like input
    location: __.cabc.Sequence[ str ] | __.Path | str
    content: __.cabc.Sequence[ int ] | bytes
    
    # Narrow returns: specific immutable types
    -> __.typx.Optional[ str ]                        # Explicit None for "not detected"
    -> tuple[ str, __.typx.Optional[ str ] ]          # Immutable tuple with concrete types
    -> __.typx.Optional[ LineSeparators ]             # Specific enum member

Type Annotation Patterns
-------------------------------------------------------------------------------

**Function Signatures:**

.. code-block:: python

    # Use Annotated for documented parameter types
    Content: __.typx.TypeAlias = __.typx.Annotated[
        bytes, 
        __.ddoc.Doc( "Raw byte content for analysis." )
    ]
    
    Location: __.typx.TypeAlias = __.typx.Annotated[
        __.typx.Union[ str, __.Path, __.cabc.Sequence[ str ] ],
        __.ddoc.Doc( "File path, URL, or path components for context." )
    ]
    
    # Comprehensive annotations with Absential pattern
    def detect_mimetype_and_charset(
        content: Content,
        location: Location, *,
        mimetype: __.Absential[ str ] = __.absent,
        charset: __.Absential[ str ] = __.absent,
    ) -> tuple[ str, __.typx.Optional[ str ] ]:

**Absential Pattern Usage:**
- Distinguish "not provided" (absent) from "explicitly None" 
- Enable three-state parameters: absent | None | value
- Preserve complex parameter handling from mimeogram

Module Organization Design
===============================================================================

Package Structure
-------------------------------------------------------------------------------

.. code-block::

    sources/detextive/
    ├── __/
    │   ├── __init__.py          # Re-exports: cabc, typx, enum, Absential
    │   ├── imports.py           # chardet, puremagic, mimetypes
    │   └── nomina.py            # Project-specific constants
    ├── __init__.py              # Public API re-exports from implementation modules
    ├── py.typed                 # Type checking marker
    ├── detection.py             # Core detection function implementations
    ├── exceptions.py            # Package exception hierarchy
    └── lineseparators.py        # LineSeparators enum and utilities

**Module Responsibilities:**

**Module Responsibilities:**

**`__init__.py` (Main Module):**
- Re-exports public API from implementation modules
- Module organization: imports → re-exports

**`detection.py`:**
- Core detection function implementations: `detect_charset`, `detect_mimetype`, `detect_mimetype_and_charset`
- Textual content validation: `is_textual_mimetype`, `is_reasonable_text_content`
- Consolidates detection logic from all source implementations

**`lineseparators.py`:**
- LineSeparators enum class with all methods
- Direct migration preserving existing byte-level detection logic
- Cross-platform line ending handling utilities

**`exceptions.py`:**
- Package exception hierarchy: Omniexception → Omnierror → specific exceptions
- Detection-specific exceptions following nomenclature patterns

**Additional Dependencies:**

The implementation will require imports for `chardet`, `mimetypes`, `puremagic` external libraries, and `dynadoc` for parameter documentation annotations.

**Private Constants Organization:**

.. code-block:: python

    # Textual MIME type patterns (consolidated from all sources)
    _TEXTUAL_MIME_TYPES = frozenset((
        'application/json',
        'application/xml', 
        'application/javascript',
        'application/ecmascript',
        'application/graphql',          # From ai-experiments
        'application/ld+json',          # From cache proxy
        'application/x-httpd-php',      # From ai-experiments
        'application/x-latex',          # From ai-experiments
        'application/x-perl',           # From mimeogram
        'application/x-python',         # From mimeogram
        'application/x-ruby',           # From mimeogram
        'application/x-shell',          # From mimeogram
        'application/x-tex',            # From ai-experiments
        'application/x-yaml',           # From cache proxy
        'application/yaml',             # From cache proxy
        'image/svg+xml',
    ))
    
    _TEXTUAL_SUFFIXES = ('+xml', '+json', '+yaml', '+toml')

Exception Hierarchy Design  
===============================================================================

Following Omniexception → Omnierror Pattern
-------------------------------------------------------------------------------

.. code-block:: python

    class Omniexception(__.immut.Object, BaseException):
        ''' Base for all exceptions raised by detextive package. '''
    
    class Omnierror(Omniexception, Exception):
        ''' Base for error exceptions raised by detextive package. '''
    
    # Specific exceptions following nomenclature patterns
    class CharsetDetectFailure( Omnierror, RuntimeError ):
        ''' Raised when character encoding detection fails. '''
    
    class ContentDecodeFailure( Omnierror, UnicodeError ):
        ''' Raised when content cannot be decoded with detected charset. '''
    
    class TextualMimetypeInvalidity( Omnierror, ValueError ):
        ''' Raised when MIME type is invalid for textual content processing. '''

Implementation Considerations
===============================================================================

Behavioral Fidelity Requirements
-------------------------------------------------------------------------------

**UTF-8 Bias Logic:**
- Prefer UTF-8 for ASCII-compatible content
- Validate detected charsets through trial decoding
- Return 'utf-8' for successful UTF-8 decoding of non-UTF charsets

**MIME Type Fallback Chain:**
- Primary: puremagic content-based detection
- Fallback: mimetypes extension-based detection
- Default: 'text/plain' if charset detected, 'application/octet-stream' otherwise

**Parameter Validation:**
- Preserve complex logic from `detect_mimetype_and_charset`
- Apply textual MIME type validation with trial decoding
- Handle mixed parameter states using Absential pattern

**Performance Characteristics:**
- Sample-based line separator detection (default 1KB limit) for performance on large files
- Lazy evaluation of detection operations
- Minimal abstraction to preserve existing performance

