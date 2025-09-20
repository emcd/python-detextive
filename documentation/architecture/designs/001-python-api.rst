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
001. Python API Specification
*******************************************************************************

Overview
===============================================================================

This document specifies the Python API implementing context-aware
text detection with pluggable backend support, confidence-based detection,
and optional dependency architecture.

The design follows established project practices for interface contracts,
module organization, naming conventions, and provides both simple string-based
APIs and confidence-aware APIs with structured result types.

Public Interface Specification
===============================================================================

Core Type Definitions
-------------------------------------------------------------------------------

**Confidence-Based Result Types**

.. code-block:: python

    class CharsetResult( __.immut.DataclassObject ):
        ''' Character set encoding with detection confidence. '''

        charset: __.typx.Annotated[
            __.typx.Optional[ str ],
            __.ddoc.Doc( ''' Detected character set encoding. May be None. ''' ),
        ]
        confidence: __.typx.Annotated[
            float, __.ddoc.Doc( ''' Detection confidence from 0.0 to 1.0. ''' )
        ]

    class MimetypeResult( __.immut.DataclassObject ):
        ''' MIME type with detection confidence. '''

        mimetype: __.typx.Annotated[
            str, __.ddoc.Doc( ''' Detected MIME type. ''' )
        ]
        confidence: __.typx.Annotated[
            float, __.ddoc.Doc( ''' Detection confidence from 0.0 to 1.0. ''' )
        ]


**Configuration Types**

.. code-block:: python

    class BehaviorTristate( __.enum.Enum ):
        ''' When to apply behavior. '''

        Never       = __.enum.auto( )
        AsNeeded    = __.enum.auto( )
        Always      = __.enum.auto( )

    class DetectFailureActions( __.enum.Enum ):
        ''' Possible responses to detection failure. '''

        Default     = __.enum.auto( )
        Error       = __.enum.auto( )

    class CodecSpecifiers( __.enum.Enum ):
        ''' Specifiers for dynamic codecs. '''

        FromInference   = __.enum.auto( )
        OsDefault       = __.enum.auto( )
        PythonDefault   = __.enum.auto( )
        UserSupplement  = __.enum.auto( )

    class Behaviors( __.immut.DataclassObject ):
        ''' How functions behave. '''

        charset_detectors_order: __.typx.Annotated[
            __.cabc.Sequence[ str ],
            __.ddoc.Doc( ''' Order in which charset detectors are applied. ''' ),
        ] = ( 'chardet', 'charset-normalizer' )

        charset_on_detect_failure: __.typx.Annotated[
            DetectFailureActions,
            __.ddoc.Doc( ''' Action to take on charset detection failure. ''' ),
        ] = DetectFailureActions.Default

        mimetype_detectors_order: __.typx.Annotated[
            __.cabc.Sequence[ str ],
            __.ddoc.Doc( ''' Order in which MIME type detectors are applied. ''' ),
        ] = ( 'magic', 'puremagic' )

        mimetype_on_detect_failure: __.typx.Annotated[
            DetectFailureActions,
            __.ddoc.Doc( ''' Action to take on MIME type detection failure. ''' ),
        ] = DetectFailureActions.Default

        charset_detect: __.typx.Annotated[
            BehaviorTristate,
            __.ddoc.Doc( ''' When to detect charset from content. ''' ),
        ] = BehaviorTristate.AsNeeded

        mimetype_detect: __.typx.Annotated[
            BehaviorTristate,
            __.ddoc.Doc( ''' When to detect MIME type from content. ''' ),
        ] = BehaviorTristate.AsNeeded

Simple String-Based Detection Functions
-------------------------------------------------------------------------------

**Character Encoding Detection**

.. code-block:: python

    def detect_charset(
        content: Content, /, *,
        behaviors: Behaviors = BEHAVIORS_DEFAULT,
        default: str = CHARSET_DEFAULT,
        supplement: __.Absential[ str ] = __.absent,
        mimetype: __.Absential[ str ] = __.absent,
        location: __.Absential[ Location ] = __.absent,
    ) -> __.typx.Optional[ str ]:
        ''' Detects character encoding.

            Returns the most likely character encoding. When configured for
            default return behavior, returns the default value on detection
            failure rather than raising an exception.
        '''

    def detect_mimetype(
        content: Content, /, *,
        behaviors: Behaviors = BEHAVIORS_DEFAULT,
        default: str = MIMETYPE_DEFAULT,
        charset: __.Absential[ str ] = __.absent,
        location: __.Absential[ Location ] = __.absent,
    ) -> str:
        ''' Detects MIME type.

            Returns the most likely MIME type. When configured for default
            return behavior, returns the default value on detection failure
            rather than raising an exception.
        '''

**Inference Functions with Context Support**

.. code-block:: python

    def infer_charset(
        content: Content, /, *,
        behaviors: Behaviors = BEHAVIORS_DEFAULT,
        charset_default: str = CHARSET_DEFAULT,
        http_content_type: __.Absential[ str ] = __.absent,
        charset_supplement: __.Absential[ str ] = __.absent,
        mimetype_supplement: __.Absential[ str ] = __.absent,
        location: __.Absential[ Location ] = __.absent,
    ) -> __.typx.Optional[ str ]:
        ''' Infers charset through various means.

            Utilizes HTTP Content-Type headers, location hints, and content
            analysis for contextual charset inference. Supports configurable
            default return behavior on inference failure.
        '''

    def infer_mimetype_charset(
        content: Content, /, *,
        behaviors: Behaviors = BEHAVIORS_DEFAULT,
        charset_default: str = CHARSET_DEFAULT,
        mimetype_default: str = MIMETYPE_DEFAULT,
        http_content_type: __.Absential[ str ] = __.absent,
        location: __.Absential[ Location ] = __.absent,
        charset_supplement: __.Absential[ str ] = __.absent,
        mimetype_supplement: __.Absential[ str ] = __.absent,
    ) -> tuple[ str, __.typx.Optional[ str ] ]:
        ''' Detects MIME type and charset with context support.

            Returns tuple of (mimetype, charset). Provides comprehensive
            detection utilizing all available context with configurable
            default behavior on detection failure.
        '''

Confidence-Based Detection Functions
-------------------------------------------------------------------------------

**Core Confidence Functions**

.. code-block:: python

    def detect_charset_confidence(
        content: Content, /, *,
        behaviors: Behaviors = BEHAVIORS_DEFAULT,
        default: str = CHARSET_DEFAULT,
        supplement: __.Absential[ str ] = __.absent,
        mimetype: __.Absential[ str ] = __.absent,
        location: __.Absential[ Location ] = __.absent,
    ) -> CharsetResult:
        ''' Detects character encoding with confidence scoring.

            Returns CharsetResult with charset and confidence level. When
            configured for default return behavior, returns default value
            with zero confidence on detection failure.
        '''

    def detect_mimetype_confidence(
        content: Content, /, *,
        behaviors: Behaviors = BEHAVIORS_DEFAULT,
        default: str = MIMETYPE_DEFAULT,
        charset: __.Absential[ str ] = __.absent,
        location: __.Absential[ Location ] = __.absent,
    ) -> MimetypeResult:
        ''' Detects MIME type with confidence scoring.

            Returns MimetypeResult with mimetype and confidence level. When
            configured for default return behavior, returns default value
            with zero confidence on detection failure.
        '''

**Advanced Confidence Inference**

.. code-block:: python

    def infer_charset_confidence(
        content: Content, /, *,
        behaviors: Behaviors = BEHAVIORS_DEFAULT,
        charset_default: str = CHARSET_DEFAULT,
        http_content_type: __.Absential[ str ] = __.absent,
        charset_supplement: __.Absential[ str ] = __.absent,
        mimetype_supplement: __.Absential[ str ] = __.absent,
        location: __.Absential[ Location ] = __.absent,
    ) -> CharsetResult:
        ''' Infers charset with confidence through various means.

            Utilizes contextual information for enhanced detection quality.
            Supports configurable default return behavior on inference failure.
        '''

    def infer_mimetype_charset_confidence(
        content: Content, /, *,
        behaviors: Behaviors = BEHAVIORS_DEFAULT,
        charset_default: str = CHARSET_DEFAULT,
        mimetype_default: str = MIMETYPE_DEFAULT,
        http_content_type: __.Absential[ str ] = __.absent,
        location: __.Absential[ Location ] = __.absent,
        charset_supplement: __.Absential[ str ] = __.absent,
        mimetype_supplement: __.Absential[ str ] = __.absent,
    ) -> tuple[ MimetypeResult, CharsetResult ]:
        ''' Detects MIME type and charset with confidence scoring.

            Returns tuple of (MimetypeResult, CharsetResult) with full
            confidence information for both detection results. Supports
            configurable default behavior on detection failure.
        '''

**Confidence Utility Functions**

.. code-block:: python

    def confidence_from_bytes_quantity(
        content: Content,
        behaviors: Behaviors = BEHAVIORS_DEFAULT
    ) -> float:
        ''' Calculates confidence score based on content length.

            Returns confidence value from 0.0 to 1.0 based on the amount
            of content available for analysis.
        '''

High-Level Decoding and Validation
-------------------------------------------------------------------------------

**Content Decoding**

.. code-block:: python

    def decode(
        content: Content, /, *,
        behaviors: Behaviors = BEHAVIORS_DEFAULT,
        profile: TextValidationProfile = PROFILE_TEXTUAL,
        charset_default: str = CHARSET_DEFAULT,
        mimetype_default: str = MIMETYPE_DEFAULT,
        http_content_type: __.Absential[ str ] = __.absent,
        location: __.Absential[ Location ] = __.absent,
        charset_supplement: __.Absential[ str ] = __.absent,
        mimetype_supplement: __.Absential[ str ] = __.absent,
    ) -> str:
        ''' High-level bytes-to-text decoding with validation.

            Performs comprehensive detection, decoding, and validation
            for robust text extraction from byte content. Supports
            configurable default values for graceful degradation.
        '''

**Textual Content Validation**

.. code-block:: python

    def is_textual_mimetype( mimetype: str ) -> bool:
        ''' Validates if MIME type represents textual content.

            Returns True for MIME types representing textual content.
        '''

    def is_valid_text(
        text: str,
        profile: TextValidationProfile = PROFILE_TEXTUAL
    ) -> bool:
        ''' Unicode-aware text validation with configurable profiles.

            Returns True for text meeting the specified validation profile.
        '''

Line Separator Processing
-------------------------------------------------------------------------------

**LineSeparators Enum** (unchanged from v1.x specification)

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
            ''' Detects line separator from byte content sample. '''

        @classmethod
        def normalize_universal( selfclass, content: str ) -> str:
            ''' Normalizes all line separators to Unix LF format. '''

        def normalize( self, content: str ) -> str:
            ''' Normalizes specific line separator to Unix LF format. '''

        def nativize( self, content: str ) -> str:
            ''' Converts Unix LF to this platform's line separator. '''

Type Annotation Patterns
===============================================================================

**Module Constants:**

.. code-block:: python

    CHARSET_DEFAULT: str = 'utf-8'
    MIMETYPE_DEFAULT: str = 'application/octet-stream'

**Common Type Aliases:**

.. code-block:: python

    Content: __.typx.TypeAlias = __.typx.Annotated[
        bytes,
        __.ddoc.Doc( "Raw byte content for analysis." )
    ]

    Location: __.typx.TypeAlias = __.typx.Annotated[
        str | __.pathlib.Path,
        __.ddoc.Doc( "File path or URL for detection context." )
    ]

**Absential Pattern for Context Parameters:**
- Distinguish "not provided" (absent) from "explicitly None"
- Enable three-state parameters: absent | None | value
- Support complex context handling for HTTP headers and supplements

**Return Type Patterns:**
- Simple APIs return `str` or `__.typx.Optional[ str ]`
- Confidence APIs return structured types: `CharsetResult`, `MimetypeResult`
- Combined APIs return immutable tuples: `tuple[ MimetypeResult, CharsetResult ]`
- Default return behavior: confidence = 0.0 indicates detection failure with fallback value

**Default Return Behavior Pattern:**
- `DetectFailureActions.Default`: Return default value with zero confidence
- `DetectFailureActions.Error`: Raise appropriate exception (legacy behavior)
- All detection functions accept `default` parameters for graceful degradation


Exception Hierarchy Design
===============================================================================

Following Omnierror Pattern
-------------------------------------------------------------------------------

.. code-block:: python

    class Omniexception(
        __.immut.Object, BaseException,
        instances_visibles = (
            '__cause__', '__context__', __.is_public_identifier ),
    ):
        ''' Base for all exceptions raised by package API. '''

    class Omnierror( Omniexception, Exception ):
        ''' Base for error exceptions raised by package API. '''

    # Detection-specific exceptions
    class CharsetDetectFailure( Omnierror, TypeError, ValueError ):
        ''' Raised when character encoding detection fails. '''

    class CharsetInferFailure( Omnierror, TypeError, ValueError ):
        ''' Raised when character encoding inference fails. '''

    class MimetypeDetectFailure( Omnierror, TypeError, ValueError ):
        ''' Raised when MIME type detection fails. '''

    class ContentDecodeFailure( Omnierror, UnicodeError ):
        ''' Raised when content cannot be decoded with detected charset. '''

**Exception Design Principles:**
- Follow nomenclature patterns: `<Noun><Verb>Failure`
- Inherit from appropriate built-in exception types
- Support location context in error messages
- Enable package-wide exception catching via `Omnierror`

Implementation Considerations
===============================================================================

Context-Aware Detection Strategy
-------------------------------------------------------------------------------

**Detection Priority Order:**
1. HTTP Content-Type headers (when available)
2. Location/filename extension analysis
3. Magic bytes content analysis
4. Fallback to defaults based on available information

**Registry-Based Backend Selection:**
- Configurable detector precedence via `Behaviors`
- Dynamic fallback when detectors return `NotImplemented`
- Support for multiple optional dependencies per detection type

**Confidence Integration:**
- Length-based confidence calculation
- Backend-specific confidence scoring
- AsNeeded behavior triggering based on confidence thresholds

**Performance Characteristics:**
- Lazy evaluation of detection operations
- Sample-based analysis for large content
- Minimal abstraction preserving detector performance