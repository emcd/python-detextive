# Architecture Documentation Updates Needed

## Executive Summary

Analysis of actual codebase vs architecture documentation reveals significant gaps. The implementation has evolved **far beyond** the original ADR scope with sophisticated detector registry architecture, confidence-based APIs, and pluggable backends that aren't documented.

## Major Discrepancies

### 1. ADR-002 Status Mismatch 🚨

**Current Status**: "Proposed (Deferred)"
**Reality**: **FULLY IMPLEMENTED**

**Implemented Features Beyond ADR Scope**:
- ✅ Pluggable detector backends (`CharsetDetector`, `MimetypeDetector` type aliases)
- ✅ Registry system (`charset_detectors`, `mimetype_detectors` dictionaries)
- ✅ Configuration via `Behaviors.charset_detectors_order` and `mimetype_detectors_order`
- ✅ Graceful degradation with `NotImplemented` return pattern
- ✅ Optional dependency handling (`charset-normalizer`, `python-magic`)
- ✅ Lazy import registration system

### 2. ADR-003 Implementation Status 🔄

**Implemented**:
- ✅ Enhanced function interfaces with context support
- ✅ HTTP Content-Type parsing and utilization
- ✅ Configurable `Behaviors` dataclass with validation control
- ✅ Context-driven detection strategy (HTTP → location → content)

**Dropped by Design Decision**:
- ❌ Error class provider pattern (removed due to type checking complexity)

**Different Implementation**:
- 📝 Result objects are `CharsetResult`/`MimetypeResult` not generic `Result(value, confidence)`

### 3. API Evolution Beyond Documentation 🚀

**New Functions Not in ADRs**:
- `infer_mimetype_charset_confidence()` - Returns `tuple[MimetypeResult, CharsetResult]`
- `detect_charset_confidence()` / `detect_mimetype_confidence()` - Individual confidence APIs
- `confidence_from_bytes_quantity()` - Length-based confidence calculation

**Core Type Evolution**:
```python
# Documented
Result(value, confidence)  # Generic

# Actual Implementation
CharsetResult(charset, confidence)    # Charset-specific
MimetypeResult(mimetype, confidence)  # MIME-specific
```

### 4. Registry Architecture (Undocumented) 🏗️

**Major Architectural Component Not Covered in ADRs**:
- Dynamic detector registration: `charset_detectors['chardet'] = _detect_via_chardet`
- Fallback iteration: Try detectors in order until success
- Import-time registration with graceful ImportError handling
- User-configurable detector precedence via `Behaviors`

## Specific Documentation Updates Required

### 1. ADR-002 Updates
- **Status**: "Proposed (Deferred)" → "Implemented"
- **Add**: Registry architecture documentation
- **Add**: Optional dependency strategy documentation
- **Update**: Component list to reflect actual implementation

### 2. ADR-003 Updates
- **Remove**: Error class provider pattern entirely
- **Update**: Result object documentation to reflect `CharsetResult`/`MimetypeResult`
- **Add**: Confidence-based API documentation

### 3. summary.rst Updates
- **Core Types**: Update `Result` references to `CharsetResult`/`MimetypeResult`
- **API List**: Add confidence-based functions
- **Data Flow**: Document registry-based detection process
- **Dependencies**: Update to reflect optional dependency architecture

### 4. Version Alignment
- **Current**: `__version__ = '1.1a0'`
- **Should Be**: `__version__ = '2.0a0'` (as confirmed by user)

### 5. New Architecture Documentation Needed

**Detector Registry Architecture** (new ADR or section):
- Type aliases for detector functions
- Registration patterns and discovery
- Fallback logic and error handling
- Configuration through Behaviors
- Optional dependency strategy

## Implementation Highlights to Document

### 1. Elegant Registry Pattern
```python
charset_detectors: Dictionary[str, CharsetDetector] = Dictionary()

def _detect_via_chardet(content, behaviors) -> CharsetResult | NotImplementedType:
    try: import chardet
    except ImportError: return NotImplemented
    # ... detection logic

charset_detectors['chardet'] = _detect_via_chardet
```

### 2. Configurable Detection Order
```python
class Behaviors:
    charset_detectors_order: Sequence[str] = ('chardet', 'charset-normalizer')
    mimetype_detectors_order: Sequence[str] = ('magic', 'puremagic')
```

### 3. Confidence-Based API Design
```python
# Simple API
charset = detect_charset(content)

# Confidence API
result = detect_charset_confidence(content)
# result.charset, result.confidence

# Combined confidence API
mimetype_result, charset_result = infer_mimetype_charset_confidence(content)
```

## Recommendations

1. **Priority 1**: ✅ **COMPLETED** - Update ADR-002 status and add registry documentation
2. **Priority 2**: ✅ **COMPLETED** - Remove error class provider from ADR-003
3. **Priority 3**: ✅ **COMPLETED** - Update summary.rst core types and API lists
4. **Priority 4**: ✅ **COMPLETED** - Bump version to 2.0a0
5. **Priority 5**: ✅ **COMPLETED** - Create comprehensive detector registry documentation

## User Feedback Integration

- ✅ Version bump to 2.0a0 acknowledged as needed
- ✅ Error class provider pattern confirmed dropped due to type checking issues
- ✅ **COMPLETED** - Documentation updates completed to reflect implementation reality

## Documentation Updates Completed

### ADR-002 Updates ✅
- **Status**: Changed from "Proposed (Deferred)" to "Implemented"
- **Added**: Comprehensive detector registry architecture documentation
- **Added**: Optional dependency strategy documentation
- **Updated**: Component list to reflect actual implementation

### ADR-003 Updates ✅
- **Removed**: Error class provider pattern references
- **Updated**: Result object documentation to reflect `CharsetResult`/`MimetypeResult`
- **Added**: Confidence-based API documentation with specific result types

### summary.rst Updates ✅
- **Core Types**: Updated `Result` references to `CharsetResult`/`MimetypeResult`
- **API List**: Added `infer_mimetype_charset_confidence()` function
- **Data Flow**: Updated to document registry-based detection process
- **Dependencies**: Updated to reflect optional dependency architecture with graceful degradation
- **Added**: Detector Registry Architecture section with comprehensive implementation details

The codebase represents a **more sophisticated architecture** than originally proposed, with excellent engineering decisions around extensibility and optional dependencies that should be properly documented.