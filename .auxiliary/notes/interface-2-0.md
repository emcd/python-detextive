# Interface Design for Detextive v2.0

## Executive Summary

Analysis of real-world integration challenges from downstream packages reveals fundamental limitations in the current functional API design. The librovore integration demonstrates expensive exception translation patterns, redundant detection calls, and inability to leverage available context (HTTP headers). This document proposes a comprehensive detection interface for v2.0 that addresses these pain points while maintaining backwards compatibility.

## Current Integration Pain Points

### Exception Translation Tax

Current pattern requires 8+ lines of boilerplate per call site:

```python
# Current: Expensive exception translation
try:
    mimetype, charset = detect_mimetype_and_charset( content_bytes, location )
    if not is_textual_content( content_bytes ):
        raise DocumentationInaccessibility( url_s, "Non-textual data" )
except TextualMimetypeInvalidity as exc:
    raise DocumentationInaccessibility( url_s, str( exc ) ) from exc
```

### Redundant Detection Overhead

Multiple function calls perform overlapping analysis:
- `detect_mimetype_and_charset()` analyzes content + location
- `is_textual_content()` re-analyzes same content  
- Custom validation functions repeat content examination

### Context Loss

Available HTTP headers cannot be utilized, forcing custom fallback implementations:

```python
# Current: Cannot leverage available HTTP context
def _detect_mimetype_with_fallback(
    content: bytes, headers: _httpx.Headers, url: str
) -> str:
    header_mimetype = _extract_mimetype_from_headers( headers )
    if header_mimetype: return header_mimetype
    return __.detext.detect_mimetype( content, url ) or ''
```

### Validation Rigidity

No control over which validations occur when, leading to unnecessary work and inappropriate error handling for specific use cases.

## Proposed v2.0 Interface

### Simplified Functions for Common Cases

For frequent charset-only detection scenarios:

```python
def detect_charset(
    content: __.typx.Annotated[
        Content, __.ddoc.Doc( "Raw byte content for charset analysis." )
    ],
    content_type: __.typx.Annotated[
        __.Absential[ str ],
        __.ddoc.Doc( "Content-Type header value for charset extraction." )
    ] = __.absent,
) -> __.typx.Annotated[
    __.typx.Optional[ str ],
    __.ddoc.Doc( "Detected charset or None for non-textual content." ),
]:
    ''' Detects character encoding for textual content decoding.
    
        Returns charset if content appears textual, None otherwise.
        Optimized for the common workflow of detecting charset to decode content.
    '''
```

### Core Data Structures

```python
from . import __

TriState: __.typx.TypeAlias = __.typx.Literal[ 'never', 'as-needed', 'always' ]


class Behaviors( __.immut.DataclassObject ):
    ''' Detection and validation behavior configuration. '''
    
    # Validation controls
    trial_decode: __.typx.Annotated[
        TriState, __.ddoc.Doc( "Control trial decoding for validation." )
    ] = 'as-needed'
    validate_printable: __.typx.Annotated[
        TriState, __.ddoc.Doc( "Control printable character validation." )
    ] = 'as-needed'
    
    # Character validation
    printable_threshold: __.typx.Annotated[
        float, __.ddoc.Doc( "Maximum fraction of non-printable characters allowed (0.0-1.0)." )
    ] = 0.0
    
    # Fallback behavior
    assume_utf8_superset: __.typx.Annotated[
        bool, __.ddoc.Doc( "Prefer UTF-8 for ASCII and suspected UTF-8 content." )
    ] = True

def detect_mimetype_charset(
    content: __.typx.Annotated[
        Content, __.ddoc.Doc( "Raw byte content for analysis." )
    ],
    location: __.typx.Annotated[
        __.Absential[ Location ],
        __.ddoc.Doc( "File path, URL, or location context." )
    ] = __.absent, *,
    content_type: __.typx.Annotated[
        __.Absential[ str ],
        __.ddoc.Doc( "Content-Type header value when available." )
    ] = __.absent,
    behaviors: __.typx.Annotated[
        __.Absential[ Behaviors ],
        __.ddoc.Doc( "Detection and validation behavior configuration." )
    ] = __.absent,
    error_class_provider: __.typx.Annotated[
        __.Absential[ ErrorClassProvider ],
        __.ddoc.Doc( "Maps exception names to downstream exception classes." )
    ] = __.absent,
) -> __.typx.Annotated[
    tuple[ __.Absential[ str ], __.Absential[ str ] ],
    __.ddoc.Doc( "Tuple of (mimetype, charset) with absent for undetectable values." ),
    __.ddoc.Raises( 
        _exceptions.Omnierror, 
        "When detection fails and error_class_provider is absent (default)." 
    ),
]:
    ''' Detects MIME type and character encoding with optional context.
    
        Detection methods selected based on available context:
        - Content-Type header (if provided): Parsing with fallback
        - Location/filename (if provided): Extension-based detection with fallback  
        - Content analysis: Magic bytes as final fallback
        
        Error class provider semantics:
        - None: Return absent values instead of raising exceptions
        - absent: Use Detextive's native exception hierarchy (default)
        - Callable: Map exception names to downstream exception classes
    '''

def detect_mimetype_charset_linesep(
    content: __.typx.Annotated[
        Content, __.ddoc.Doc( "Raw byte content for analysis." )
    ],
    location: __.typx.Annotated[
        __.Absential[ Location ],
        __.ddoc.Doc( "File path, URL, or location context." )
    ] = __.absent, *,
    content_type: __.typx.Annotated[
        __.Absential[ str ],
        __.ddoc.Doc( "Content-Type header value when available." )
    ] = __.absent,
    behaviors: __.typx.Annotated[
        __.Absential[ Behaviors ],
        __.ddoc.Doc( "Detection and validation behavior configuration." )
    ] = __.absent,
    error_class_provider: __.typx.Annotated[
        __.Absential[ ErrorClassProvider ],
        __.ddoc.Doc( "Maps exception names to downstream exception classes." )
    ] = __.absent,
) -> __.typx.Annotated[
    tuple[ __.Absential[ str ], __.Absential[ str ], __.Absential[ LineSeparators ] ],
    __.ddoc.Doc( "Tuple of (mimetype, charset, line_separator) with absent for undetectable values." ),
    __.ddoc.Raises( 
        _exceptions.Omnierror, 
        "When detection fails and error_class_provider is absent (default)." 
    ),
]:
    ''' Detects MIME type, character encoding, and line separators.
    
        Comprehensive detection for text processing workflows requiring
        all three pieces of information.
    '''
```

### Error Class Provider Pattern

```python
ErrorClassProvider: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[ [ str ], type[ Exception ] ],
    __.ddoc.Doc(
        ''' Maps exception class names to downstream exception types.
        
            Enables zero-boilerplate exception translation by allowing
            downstream packages to provide their own exception hierarchies.
            
            Example: lambda name: DocumentationInaccessibility
        '''
    ),
]
```

### Integration Transformation

Current integration pattern:

```python
# Before: Multiple calls + exception handling (8+ lines)
try:
    mimetype, charset = detect_mimetype_and_charset( content_bytes, location )
    if not is_textual_content( content_bytes ):
        raise DocumentationInaccessibility( url_s, "Non-textual data" )
except TextualMimetypeInvalidity as exc:
    raise DocumentationInaccessibility( url_s, str( exc ) ) from exc
```

Proposed pattern:

```python  
# After: Single call, zero boilerplate
mimetype, charset = detect_mimetype_charset(
    content_bytes, location,
    content_type = response.headers.get( 'content-type' ),
    error_class_provider = lambda name: DocumentationInaccessibility
)
```

## Backwards Compatibility Strategy

### Enhanced Function Implementation

Current functions enhanced with new capabilities:

```python
def detect_mimetype_and_charset(
    content: Content, 
    location: Location, *,
    mimetype: __.Absential[ str ] = __.absent,
    charset: __.Absential[ str ] = __.absent,
) -> tuple[ str, __.typx.Optional[ str ] ]:
    ''' Combined MIME type and charset detection.
    
        Enhanced in v2.0 with improved context-aware detection.
    '''
```

### Migration Benefits

- **Zero Breaking Changes**: Existing code continues working
- **Enhanced Capabilities**: Existing functions gain HTTP context awareness
- **New Function Options**: `detect_charset` and `detect_mimetype_charset_linesep` for specific workflows
- **Error Class Provider**: All functions support custom exception hierarchies

## Architectural Recommendations

### Function Dependency Hierarchy

Focus on core functions that people actually use:

```
┌─────────────────────────────────────────────────────┐
│                 Layer 3: Public API                │  
│  detect_charset()  detect_mimetype_charset()       │
│        detect_mimetype_charset_linesep()            │
│          (enhanced v1 functions)                    │
└─────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────┐
│           Layer 2: Validation Functions             │
│  _validate_charset()  _validate_printable()  etc... │
└─────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────┐  
│          Layer 1: Primitive Detectors              │
│ _detect_mimetype_from_magic()  _detect_from_headers()  etc.. │
└─────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

1. **Enhanced Existing Functions**: Current API enhanced with context awareness
2. **Context-Driven Detection**: Use HTTP headers first, then location, then magic bytes based on what's provided
3. **Conditional Execution**: Only call primitives/validators needed based on `Behaviors`
4. **Shared Validation**: Validation functions work with any detection source
5. **Focused Interface**: Three core functions cover real-world use cases

### Performance Optimizations

- **Context Fusion**: HTTP headers + content analysis in single pass
- **Validation Control**: Skip unnecessary validation based on use case
- **Optimized Workflows**: `detect_charset` for decoding, full detection when needed

## Implementation Considerations

### Default Behaviors Configuration

Optimize for common cases requiring zero configuration:

```python
BEHAVIORS_DEFAULT = Behaviors(
    trial_decode = 'as-needed',
    validate_printable = 'as-needed',
    printable_threshold = 0.0,
    assume_utf8_superset = True,
)
```


### Magic Detection Enhancement

Consider supporting `python-magic` (libmagic bindings) as optional dependency with `puremagic` fallback for improved format coverage.

### Testing Strategy

Behaviors matrix creates large test space requiring systematic approach:

```python
@pytest.mark.parametrize( 'trial_decode', [ 'never', 'as-needed', 'always' ] )
@pytest.mark.parametrize( 'validate_printable', [ 'never', 'as-needed', 'always' ] )
@pytest.mark.parametrize( 'printable_threshold', [ 0.0, 0.1, 0.2 ] )
def test_behaviors_matrix( trial_decode, validate_printable, printable_threshold ):
    ''' Tests behavior combinations systematically. '''
    behaviors = Behaviors(
        trial_decode = trial_decode,
        validate_printable = validate_printable,
        printable_threshold = printable_threshold,
    )
    # Test specific behavior combination
```

## Conclusion

This v2.0 interface proposal addresses fundamental integration pain points demonstrated by real-world usage while maintaining backwards compatibility. The error class provider pattern eliminates exception translation tax, context-aware detection reduces redundant analysis, and three focused functions cover the real-world use cases:

- `detect_charset()` - For simple content decoding workflows
- `detect_mimetype_charset()` - For content processing requiring both pieces  
- `detect_mimetype_charset_linesep()` - For comprehensive text processing

The enhanced existing functions gain HTTP context awareness without breaking changes, while the simplified `Behaviors` configuration focuses on validation controls rather than complex detection orchestration. This approach delivers immediate value through more efficient integration patterns while maintaining the functional simplicity that makes Detextive effective.