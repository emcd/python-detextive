# API Design

## 001. Python API Specification

### Overview

This document specifies the Python API implementing context-aware
text detection with pluggable backend support, confidence-based detection,
and optional dependency architecture.

The design follows established project practices for interface contracts,
module organization, naming conventions, and provides both simple string-based
APIs and confidence-aware APIs with structured result types.

### Public Interface Specification

#### Core Type Definitions

**Confidence-Based Result Types**

```python
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
```

**Configuration Types**

```python
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
```

#### Simple String-Based Detection Functions

**Character Encoding Detection**

```python
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
```

**Inference Functions with Context Support**

```python
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
```

#### Confidence-Based Detection Functions

**Core Confidence Functions**

```python
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
```

**Advanced Confidence Inference**

```python
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
```

**Confidence Utility Functions**

```python
def confidence_from_bytes_quantity(
    content: Content,
    behaviors: Behaviors = BEHAVIORS_DEFAULT
) -> float:
    ''' Calculates confidence score based on content length.

        Returns confidence value from 0.0 to 1.0 based on the amount
        of content available for analysis.
    '''
```

#### High-Level Decoding and Validation

**Content Decoding**

```python
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
```

**Textual Content Validation**

```python
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
```

#### Line Separator Processing

**LineSeparators Enum** (unchanged from v1.x specification)

```python
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
```

### Type Annotation Patterns

**Module Constants:**

```python
CHARSET_DEFAULT: str = 'utf-8'
MIMETYPE_DEFAULT: str = 'application/octet-stream'
```

**Common Type Aliases:**

```python
Content: __.typx.TypeAlias = __.typx.Annotated[
    bytes,
    __.ddoc.Doc( "Raw byte content for analysis." )
]

Location: __.typx.TypeAlias = __.typx.Annotated[
    str | __.pathlib.Path,
    __.ddoc.Doc( "File path or URL for detection context." )
]
```

**Absential Pattern for Context Parameters:**
\- Distinguish "not provided" (absent) from "explicitly None"
\- Enable three-state parameters: absent | None | value
\- Support complex context handling for HTTP headers and supplements

**Return Type Patterns:**
\- Simple APIs return `str` or `__.typx.Optional[ str ]`
\- Confidence APIs return structured types: `CharsetResult`, `MimetypeResult`
\- Combined APIs return immutable tuples: `tuple[ MimetypeResult, CharsetResult ]`
\- Default return behavior: confidence = 0.0 indicates detection failure with fallback value

**Default Return Behavior Pattern:**
\- `DetectFailureActions.Default`: Return default value with zero confidence
\- `DetectFailureActions.Error`: Raise appropriate exception (legacy behavior)
\- All detection functions accept `default` parameters for graceful degradation

### Exception Hierarchy Design

#### Following Omnierror Pattern

```python
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
```

**Exception Design Principles:**
\- Follow nomenclature patterns: `<Noun><Verb>Failure`
\- Inherit from appropriate built-in exception types
\- Support location context in error messages
\- Enable package-wide exception catching via `Omnierror`

### Implementation Considerations

#### Context-Aware Detection Strategy

**Detection Priority Order:**
1\. HTTP Content-Type headers (when available)
2\. Location/filename extension analysis
3\. Magic bytes content analysis
4\. Fallback to defaults based on available information

**Registry-Based Backend Selection:**
\- Configurable detector precedence via `Behaviors`
\- Dynamic fallback when detectors return `NotImplemented`
\- Support for multiple optional dependencies per detection type

**Confidence Integration:**
\- Length-based confidence calculation
\- Backend-specific confidence scoring
\- AsNeeded behavior triggering based on confidence thresholds

**Performance Characteristics:**
\- Lazy evaluation of detection operations
\- Sample-based analysis for large content
\- Minimal abstraction preserving detector performance



## 002. Detector Registry Specification

### Overview

This document specifies the detector registry architecture for pluggable
backend support in the detextive library. The registry system enables
configurable detector precedence, graceful degradation with optional
dependencies, and dynamic fallback strategies for robust detection across
diverse environments.

The design follows established project practices for type aliases, interface
contracts, and module organization while providing extensibility for
third-party detection backends.

### Registry Architecture

#### Core Registry Types

**Detector Function Signatures**

```python
CharsetDetector: __.typx.TypeAlias = __.cabc.Callable[
    [ Content, Behaviors ],
    CharsetResult | __.types.NotImplementedType
]

MimetypeDetector: __.typx.TypeAlias = __.cabc.Callable[
    [ Content, Behaviors ],
    MimetypeResult | __.types.NotImplementedType
]
```

**Registry Container Types**

```python
charset_detectors: __.accret.Dictionary[ str, CharsetDetector ]
mimetype_detectors: __.accret.Dictionary[ str, MimetypeDetector ]
```

**Registry Contract Specifications:**
\- Detectors return specific result types with confidence scoring
\- `NotImplemented` return value indicates missing optional dependency
\- Registry keys provide user-configurable detector ordering
\- Detector functions accept standardized parameters for consistent interfaces

#### Registry Registration Pattern

**Dynamic Registration System**

```python
def _detect_via_chardet(
    content: Content, behaviors: Behaviors
) -> CharsetResult | __.types.NotImplementedType:
    ''' Detects charset using chardet library. '''
    try:
        from chardet import detect as _chardet_detect
    except ImportError:
        return NotImplemented

    # Detection implementation would follow here

def _detect_via_charset_normalizer(
    content: Content, behaviors: Behaviors
) -> CharsetResult | __.types.NotImplementedType:
    ''' Detects charset using charset-normalizer library. '''
    try:
        from charset_normalizer import from_bytes
    except ImportError:
        return NotImplemented

    # Detection implementation would follow here

# Registration at module initialization
charset_detectors[ 'chardet' ] = _detect_via_chardet
charset_detectors[ 'charset-normalizer' ] = _detect_via_charset_normalizer
```

**Registration Design Principles:**
\- Lazy import strategy with graceful ImportError handling
\- Consistent function signature across all detector implementations
\- Registry key naming matches common library names for intuitive configuration
\- Module-level registration enables import-time detector discovery

### Optional Dependency Strategy

#### Graceful Degradation Pattern

**NotImplemented Return Protocol**

The registry system implements graceful degradation where:
\- Detectors return `NotImplemented` for missing optional dependencies
\- Registry iteration continues until successful detection
\- Exception raising occurs only when all configured detectors fail
\- User-configurable detector ordering enables fallback preferences

#### Configuration Integration

**Behavior-Driven Detector Selection**

```python
class Behaviors( __.immut.DataclassObject ):
    ''' Configuration for detector registry usage. '''

    charset_detectors_order: __.typx.Annotated[
        __.cabc.Sequence[ str ],
        __.ddoc.Doc( ''' Order in which charset detectors are applied. ''' ),
    ] = ( 'chardet', 'charset-normalizer' )

    mimetype_detectors_order: __.typx.Annotated[
        __.cabc.Sequence[ str ],
        __.ddoc.Doc( ''' Order in which MIME type detectors are applied. ''' ),
    ] = ( 'magic', 'puremagic' )
```

**Configuration Design Features:**
\- User-configurable detector precedence through sequence ordering
\- Default ordering based on library reliability and performance characteristics
\- Runtime modification support for dynamic behavior adjustment
\- Validation ensures only registered detectors attempted

### Multiple Backend Support

#### Charset Detection Backends

**Supported Charset Libraries**

```python
# Standard charset detection backends
charset_detectors[ 'chardet' ]              # Statistical analysis, UTF-8 bias
charset_detectors[ 'charset-normalizer' ]   # Enhanced heuristics, multiple algorithms
```

**Backend Characteristics:**
\- `chardet`: Mature statistical analysis with proven UTF-8 bias handling
\- `charset-normalizer`: Enhanced detection algorithms with multiple confidence scoring

**Registration Strategy:**
\- Both libraries registered with graceful ImportError handling
\- Default ordering prioritizes `chardet` for proven reliability
\- User configuration enables alternative precedence based on use case requirements

#### MIME Type Detection Backends

**Supported MIME Type Libraries**

```python
# MIME type detection backends
mimetype_detectors[ 'magic' ]      # python-magic (libmagic bindings)
mimetype_detectors[ 'puremagic' ]  # Pure Python magic byte detection
```

**Backend Selection Strategy:**
\- `python-magic`: Comprehensive magic byte database via libmagic
\- `puremagic`: Pure Python implementation for deployment simplicity
\- Fallback ordering ensures detection capability across diverse environments

**Detection Priority Logic:**
\- Primary detection via content analysis (magic bytes)
\- Secondary detection via filename extension analysis
\- Default MIME type assignment based on available context

### Interface Contract Design

#### Detector Function Contracts

**Standardized Parameters**

```python
def detector_function(
    content: Content,           # Raw byte content for analysis
    behaviors: Behaviors        # Configuration object with detection preferences
) -> DetectionResult | __.types.NotImplementedType:
    ''' Standard detector function signature. '''
```

**Return Value Specifications:**
\- Successful detection returns structured result with confidence scoring
\- Missing dependencies indicated by `NotImplemented` return value
\- Exception raising reserved for genuine detection failures
\- Result types provide consistent interface across all detection backends

**Parameter Design Principles:**
\- Wide parameter acceptance for maximum backend flexibility
\- Behavior-driven configuration enables detector-specific optimization
\- Content parameter accepts any bytes-like input for broad compatibility

#### Result Type Integration

**Registry Return Value Contracts:**
\- Successful detection returns `CharsetResult` or `MimetypeResult` (defined in API design)
\- Missing dependencies indicated by `NotImplemented` return value
\- Exception raising reserved for genuine detection failures
\- Confidence scoring enables quality-based selection among multiple results

### Registry Architecture Summary

**Key Design Features:**
\- Pluggable backend system with standardized detector function signatures
\- Graceful degradation through `NotImplemented` return protocol
\- User-configurable detector precedence via `Behaviors` configuration
\- Support for multiple optional dependencies per detection type

**Implementation Architecture:**
\- Registry containers in `detectors.py` module
\- Type aliases for detector function signatures
\- Dynamic registration with import-time discovery
\- Registry-based dispatch in core detection functions



## 003. Default Return Behavior Specification

### Overview

This document specifies configurable failure handling through default value
returns as an alternative to exception-based error handling. The design
enables graceful degradation for detection failures while maintaining
backward compatibility.

The pattern addresses performance-critical scenarios, defensive programming
patterns, and fallback value workflows where detection failures are expected
and should not interrupt processing flows.

### Core Design Principles

#### Configurable Failure Strategy

**DetectFailureActions Enum Specification**

```python
class DetectFailureActions( __.enum.Enum ):
    ''' Possible responses to detection failure. '''

    Default     = __.enum.auto( )
    Error       = __.enum.auto( )
```

**Failure Action Semantics:**

- **Default**: Return configurable default value with zero confidence
- **Error**: Raise appropriate exception (preserves backward compatibility)

**Configuration Integration**

The failure handling strategy integrates with the `Behaviors`
configuration pattern:

```python
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
```

### Default Value Management

#### System-Wide Default Constants

**Module-Level Constants:**

```python
CHARSET_DEFAULT: str = 'utf-8'
MIMETYPE_DEFAULT: str = 'application/octet-stream'
```

**Default Value Parameters:**

All detection functions accept optional `default` parameters with appropriate
module-level constants as defaults.

**Confidence Scoring for Default Returns:**

When returning default values due to detection failure:

- **Confidence Score**: Always `0.0` to indicate detection failure
- **Clear Distinction**: Enables differentiation between successful low-confidence detection and failure fallback
- **Programmatic Detection**: Applications can check `result.confidence == 0.0` to identify fallback scenarios

### Core Behavior Specification

**Failure Mode Selection:**

- **Default Mode**: Return `default` parameter value with zero confidence on detection failure
- **Error Mode**: Raise appropriate exception on detection failure (preserves compatibility)

**Multi-Detection Handling:**

- **Independent Failure Actions**: Each detection type uses its own failure action configuration
- **Separate Default Values**: `charset_default` and `mimetype_default` parameters
- **Granular Control**: Mixed failure modes supported (e.g., charset defaults, mimetype errors)

### Usage Patterns and Integration

#### Performance-Critical Workflows

**Batch Processing Configuration:**

```python
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
```

**Zero-Exception Processing:**

Eliminates exception handling overhead for expected failure scenarios:

```python
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
```

#### Defensive Programming Patterns

**Robust Content Processing:**

```python
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
```

**Mixed Error Handling:**

```python
# Strict validation for charset, graceful for MIME type
mixed_behaviors = Behaviors(
    charset_on_detect_failure = DetectFailureActions.Error,
    mimetype_on_detect_failure = DetectFailureActions.Default,
)
```

#### Security-Conscious Integration

**Validation-First Configuration:**

```python
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
```

### Implementation Integration Points

#### Detector Registry Integration

**Registry Failure Handling:**

The default return behavior integrates with the detector registry architecture:

```python
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
```

**Optional Dependency Graceful Degradation:**

When preferred detectors are unavailable, the system gracefully falls back:

```python
def _detect_via_chardet( content: Content, behaviors: Behaviors ) -> CharsetResult | NotImplementedType:
    try: import chardet
    except ImportError: return NotImplemented
    # ... detection logic

# Registry automatically handles NotImplemented returns
# Falls back to next detector or applies failure action
```

#### Confidence-Based Decision Making

**Confidence Threshold Integration:**

Default return behavior works with existing confidence-based logic:

```python
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
```

### Backward Compatibility Guarantees

#### API Compatibility

**Signature Preservation:**

- All existing function signatures remain valid
- New `default` parameters have appropriate defaults
- Existing code continues working without modification

**Behavioral Preservation:**

- Default configuration preserves exception-based error handling for simple functions
- Confidence functions default to graceful degradation pattern
- No breaking changes to existing exception types or messages

**Migration Path:**

```python
# v1.x/v2.0 existing code (continues working)
try:
    charset = detect_charset( content )
except CharsetDetectFailure:
    charset = 'utf-8'  # Manual fallback

# Enhanced v2.x approach (optional migration)
behaviors = Behaviors( charset_on_detect_failure = DetectFailureActions.Default )
charset = detect_charset( content, behaviors = behaviors, default = 'utf-8' )
# No exception handling needed
```

#### Configuration Evolution

**Behaviors Dataclass Compatibility:**

- New fields added with backward-compatible defaults
- Existing `Behaviors` instances continue working
- Incremental adoption of new failure handling features

**Exception Hierarchy Preservation:**

- All existing exception classes maintained
- Exception chaining and context preservation unchanged
- Error messages and exception attributes consistent

### Type Safety and Documentation

#### Type Annotation Patterns

**Confidence Score Interpretation:**

```python
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
```

**Default Parameter Type Safety:**

All `default` parameters are properly typed as `str` with appropriate
module-level constants as defaults, ensuring type safety and consistency.

#### Documentation Patterns

**Function Documentation Standards:**

All function docstrings include failure behavior documentation:

```python
def detect_charset_confidence( ... ) -> CharsetResult:
    ''' Detects character encoding with confidence scoring.

        When configured for default return behavior, returns default
        value with zero confidence on detection failure rather than
        raising CharsetDetectFailure. Confidence of 0.0 indicates
        detection failure with fallback value.
    '''
```

**Configuration Documentation:**

`Behaviors` fields include comprehensive documentation of failure handling semantics and integration with other configuration options.
