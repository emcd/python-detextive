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
   | +--------------------------------------------------------------------------+


*******************************************************************************
003. Default Return Behavior Specification
*******************************************************************************

Overview
===============================================================================

This document specifies configurable failure handling through default value
returns as an alternative to exception-based error handling. The design
enables graceful degradation for detection failures while maintaining
backward compatibility.

The pattern addresses performance-critical scenarios, defensive programming
patterns, and fallback value workflows where detection failures are expected
and should not interrupt processing flows.

Core Design Principles
===============================================================================

Configurable Failure Strategy
-------------------------------------------------------------------------------

**DetectFailureActions Enum Specification**

.. code-block:: python

    class DetectFailureActions( __.enum.Enum ):
        ''' Possible responses to detection failure. '''

        Default     = __.enum.auto( )
        Error       = __.enum.auto( )

**Failure Action Semantics:**

- **Default**: Return configurable default value with zero confidence
- **Error**: Raise appropriate exception (preserves backward compatibility)

**Configuration Integration**

The failure handling strategy integrates with the ``Behaviors``
configuration pattern:

.. code-block:: python

    class Behaviors( __.immut.DataclassObject ):
        ''' How functions behave. '''

        charset_on_detect_failure: __.typx.Annotated[
            DetectFailureActions,
            __.ddoc.Doc( ''' Action to take on charset detection failure. ''' ),
        ] = DetectFailureActions.Default

        mimetype_on_detect_failure: __.typx.Annotated[
            DetectFailureActions,
            __.ddoc.Doc( ''' Action to take on MIME type detection failure. ''' ),
        ] = DetectFailureActions.Default

Default Value Management
===============================================================================

System-Wide Default Constants
-------------------------------------------------------------------------------

**Module-Level Constants:**

.. code-block:: python

    CHARSET_DEFAULT: str = 'utf-8'
    MIMETYPE_DEFAULT: str = 'application/octet-stream'

**Default Value Parameters:**

All detection functions accept optional ``default`` parameters with appropriate
module-level constants as defaults.

**Confidence Scoring for Default Returns:**

When returning default values due to detection failure:

- **Confidence Score**: Always ``0.0`` to indicate detection failure
- **Clear Distinction**: Enables differentiation between successful low-confidence detection and failure fallback
- **Programmatic Detection**: Applications can check ``result.confidence == 0.0`` to identify fallback scenarios

Core Behavior Specification
===============================================================================

**Failure Mode Selection:**

- **Default Mode**: Return ``default`` parameter value with zero confidence on detection failure
- **Error Mode**: Raise appropriate exception on detection failure (preserves compatibility)

**Multi-Detection Handling:**

- **Independent Failure Actions**: Each detection type uses its own failure action configuration
- **Separate Default Values**: ``charset_default`` and ``mimetype_default`` parameters
- **Granular Control**: Mixed failure modes supported (e.g., charset defaults, mimetype errors)

Usage Patterns and Integration
===============================================================================

Performance-Critical Workflows
-------------------------------------------------------------------------------

**Batch Processing Configuration:**

.. code-block:: python

    # Configure for maximum performance with graceful degradation
    performance_behaviors = Behaviors(
        charset_on_detect_failure = DetectFailureActions.Default,
        mimetype_on_detect_failure = DetectFailureActions.Default,
        trial_decode = BehaviorTristate.Never,
        text_validate = BehaviorTristate.Never,
    )

    for content_item in large_content_batch:
        result = detect_charset_confidence(
            content_item,
            behaviors = performance_behaviors,
            default = 'utf-8'  # Project-specific default
        )
        if result.confidence > 0.0:
            # Use detected charset
            charset = result.charset
        else:
            # Handle graceful fallback
            charset = result.charset  # Project default

**Zero-Exception Processing:**

Eliminates exception handling overhead for expected failure scenarios:

.. code-block:: python

    def process_content_batch( contents: list[ bytes ] ) -> list[ str ]:
        ''' Processes content batch without exception handling. '''
        texts = [ ]
        for content in contents:
            charset_result = detect_charset_confidence( content )
            if charset_result.confidence > 0.0:
                # High-confidence detection
                text = content.decode( charset_result.charset )
            else:
                # Fallback to default encoding
                text = content.decode( charset_result.charset, errors = 'replace' )
            texts.append( text )
        return texts

Defensive Programming Patterns
-------------------------------------------------------------------------------

**Robust Content Processing:**

.. code-block:: python

    def safe_text_extraction( content: bytes ) -> str:
        ''' Extracts text with multiple fallback layers. '''
        charset_result = detect_charset_confidence( content )

        # Layer 1: High-confidence detection
        if charset_result.confidence > 0.8:
            try: return content.decode( charset_result.charset )
            except UnicodeDecodeError: pass

        # Layer 2: Medium-confidence with error handling
        if charset_result.confidence > 0.3:
            try: return content.decode( charset_result.charset, errors = 'replace' )
            except UnicodeDecodeError: pass

        # Layer 3: Fallback to system default
        return content.decode( charset_result.charset, errors = 'ignore' )

**Mixed Error Handling:**

.. code-block:: python

    # Strict validation for charset, graceful for MIME type
    mixed_behaviors = Behaviors(
        charset_on_detect_failure = DetectFailureActions.Error,
        mimetype_on_detect_failure = DetectFailureActions.Default,
    )

Security-Conscious Integration
-------------------------------------------------------------------------------

**Validation-First Configuration:**

.. code-block:: python

    # Security-focused configuration with exception-based error handling
    security_behaviors = Behaviors(
        charset_on_detect_failure = DetectFailureActions.Error,
        mimetype_on_detect_failure = DetectFailureActions.Error,
        trial_decode = BehaviorTristate.Always,
        text_validate = BehaviorTristate.Always,
    )

    try:
        result = detect_charset_confidence(
            untrusted_content,
            behaviors = security_behaviors
        )
        # Proceed only with successful detection
        validated_text = process_with_charset( result.charset )
    except CharsetDetectFailure:
        # Handle detection failure as security concern
        reject_untrusted_content( )

Implementation Integration Points
===============================================================================

Detector Registry Integration
-------------------------------------------------------------------------------

**Registry Failure Handling:**

The default return behavior integrates with the detector registry architecture:

.. code-block:: python

    # Registry iteration with failure handling
    for detector_name in behaviors.charset_detectors_order:
        detector = charset_detectors.get( detector_name )
        if detector is None: continue
        result = detector( content, behaviors )
        if result is NotImplemented: continue
        return result

    # No detectors succeeded - apply failure action
    match behaviors.charset_on_detect_failure:
        case DetectFailureActions.Default:
            return CharsetResult( charset = default, confidence = 0.0 )
        case DetectFailureActions.Error:
            raise CharsetDetectFailure( location = location )

**Optional Dependency Graceful Degradation:**

When preferred detectors are unavailable, the system gracefully falls back:

.. code-block:: python

    def _detect_via_chardet( content: Content, behaviors: Behaviors ) -> CharsetResult | NotImplementedType:
        try: import chardet
        except ImportError: return NotImplemented
        # ... detection logic

    # Registry automatically handles NotImplemented returns
    # Falls back to next detector or applies failure action

Confidence-Based Decision Making
-------------------------------------------------------------------------------

**Confidence Threshold Integration:**

Default return behavior works with existing confidence-based logic:

.. code-block:: python

    # AsNeeded behavior respects confidence scoring
    charset_result = detect_charset_confidence( content )

    if charset_result.confidence >= behaviors.trial_decode_confidence:
        # Skip expensive trial decode for high-confidence results
        return charset_result
    elif charset_result.confidence == 0.0:
        # Handle failure case explicitly
        return fallback_charset_detection( content )
    else:
        # Perform trial decode for medium-confidence results
        return trial_decode_validation( content, charset_result )

Backward Compatibility Guarantees
===============================================================================

API Compatibility
-------------------------------------------------------------------------------

**Signature Preservation:**

- All existing function signatures remain valid
- New ``default`` parameters have appropriate defaults
- Existing code continues working without modification

**Behavioral Preservation:**

- Default configuration preserves exception-based error handling for simple functions
- Confidence functions default to graceful degradation pattern
- No breaking changes to existing exception types or messages

**Migration Path:**

.. code-block:: python

    # v1.x/v2.0 existing code (continues working)
    try:
        charset = detect_charset( content )
    except CharsetDetectFailure:
        charset = 'utf-8'  # Manual fallback

    # Enhanced v2.x approach (optional migration)
    behaviors = Behaviors( charset_on_detect_failure = DetectFailureActions.Default )
    charset = detect_charset( content, behaviors = behaviors, default = 'utf-8' )
    # No exception handling needed

Configuration Evolution
-------------------------------------------------------------------------------

**Behaviors Dataclass Compatibility:**

- New fields added with backward-compatible defaults
- Existing ``Behaviors`` instances continue working
- Incremental adoption of new failure handling features

**Exception Hierarchy Preservation:**

- All existing exception classes maintained
- Exception chaining and context preservation unchanged
- Error messages and exception attributes consistent

Type Safety and Documentation
===============================================================================

Type Annotation Patterns
-------------------------------------------------------------------------------

**Confidence Score Interpretation:**

.. code-block:: python

    def interpret_charset_result( result: CharsetResult ) -> str:
        ''' Interprets charset result with confidence awareness. '''
        if result.confidence == 0.0:
            # Detection failed - using fallback value
            logger.warning( f"Charset detection failed, using fallback: {result.charset}" )
        elif result.confidence < 0.5:
            # Low confidence detection
            logger.info( f"Low-confidence charset detection: {result.charset}" )
        # Normal high-confidence processing
        return result.charset

**Default Parameter Type Safety:**

All ``default`` parameters are properly typed as ``str`` with appropriate
module-level constants as defaults, ensuring type safety and consistency.

Documentation Patterns
-------------------------------------------------------------------------------

**Function Documentation Standards:**

All function docstrings include failure behavior documentation:

.. code-block:: python

    def detect_charset_confidence( ... ) -> CharsetResult:
        ''' Detects character encoding with confidence scoring.

            When configured for default return behavior, returns default
            value with zero confidence on detection failure rather than
            raising CharsetDetectFailure. Confidence of 0.0 indicates
            detection failure with fallback value.
        '''

**Configuration Documentation:**

``Behaviors`` fields include comprehensive documentation of failure handling semantics and integration with other configuration options.