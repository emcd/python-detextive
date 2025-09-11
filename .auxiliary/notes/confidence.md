# Confidence-Based Detection System

## Summary

This document outlines the planned confidence-based detection system for Detextive v2.0, designed to make `AsNeeded` behavior in `BehaviorTristate` more intelligent by using confidence scores to determine when to skip expensive operations like trial decodes and text validation.

## Core Concept

Currently, `AsNeeded` logic is either not implemented or uses arbitrary heuristics. The confidence system introduces quantitative scoring (0.0-1.0) to make these decisions data-driven:

- **High confidence** → Skip expensive validation (trust the detection)
- **Low confidence** → Perform additional validation (trial decode, text validation)

## Key Design Decisions

### 1. **Granular DTO Attributes**
```python
class Behaviors(__.immut.Dataclass):
    # ... existing fields ...
    
    trial_decode_confidence_limit: float = 0.7
    validate_confidence_limit: float = 0.8
```

**Rationale**: Separate thresholds allow different risk tolerances - trial decode can be more aggressive than text validation.

### 2. **Composite Confidence Scoring**
```python
def calculate_composite_confidence(
    mimetype_result: DetectionResult,
    charset_result: DetectionResult
) -> float:
    return mimetype_result.confidence * charset_result.confidence
```

**Rationale**: Uncertainty compounds - if mimetype detection is 80% confident and charset is 90% confident, total confidence is 72%.

### 3. **Sequence-Based Results**
```python
@dataclass
class DetectionResult:
    value: str
    confidence: float
    source: str = ''

def detect_charset_candidates(content, behaviors) -> list[DetectionResult]:
    """Return ranked list of charset candidates."""

def detect_mimetype_candidates(content, behaviors) -> list[DetectionResult]:
    """Return ranked list of mimetype candidates."""
```

**Benefits**: 
- `chardet.detect_all()` provides multiple candidates with confidence scores
- Can pass multiple high-confidence candidates to `attempt_decodes()` 
- More robust than single-candidate approach
- **Public API** - exposes candidate detection for advanced use cases

### 4. **Length-Based Mimetype Confidence** 
For `puremagic` (which doesn't expose confidence directly):
```python
confidence = min(1.0, len(content) / 1024.0)
```

**Rationale**: Magic byte detection is more reliable with larger samples. Full confidence at 1KB+, proportional below.

## Implementation Architecture

### Phase 1: Core Confidence System
1. **DetectionResult dataclass** - standardize confidence reporting
2. **Update detector signatures** - return confidence with results  
3. **Smart AsNeeded logic** - use confidence thresholds for decisions
4. **Multi-candidate support** - pass sequence of candidates to decoders

### Phase 2: Enhanced Detection Functions
```python
def infer_mimetype_charset(
    content: Content, /, *,
    behaviors: Behaviors = BEHAVIORS_DEFAULT,
    **kwargs
) -> tuple[str, str]:  # mimetype, charset (existing signature)
    """Existing function enhanced with confidence-based AsNeeded logic."""
    
    # Use new candidate detection functions internally
    mimetype_candidates = detect_mimetype_candidates(content, behaviors, **kwargs)
    charset_candidates = detect_charset_candidates(content, behaviors, **kwargs)
    
    # Smart AsNeeded logic using confidence thresholds
    for charset_candidate in charset_candidates:
        composite_conf = calculate_composite_confidence(
            mimetype_candidates[0], charset_candidate)
        
        if behaviors.trial_decode_confidence >= composite_conf:
            # Low confidence - perform trial decode (existing behavior)
            charset = _trial_decode_as_necessary(...)
        else:
            # High confidence - trust detection
            charset = charset_candidate.value
            
        return mimetype_candidates[0].value, charset
```

**Benefits of adapting existing functions:**
- **Backward compatible** - no signature changes to public API
- **Cleaner architecture** - confidence is internal implementation detail
- **Easier migration** - existing code continues working unchanged

### Phase 3: Multiple Backend Support (Future)
Add `mimetype_detector_precedence` to Behaviors DTO to choose between `puremagic`, `python-magic`, etc.

## Smart AsNeeded Behavior Examples

### Trial Decode Decision
```python
# High confidence (0.8 × 0.9 = 0.72 > 0.7 threshold)
if composite_confidence >= behaviors.trial_decode_confidence_limit:
    charset = charset_candidate.value  # Trust detection
else:
    charset = _trial_decode_as_necessary(...)  # Verify with decode
```

### Text Validation Decision  
```python
# Lower confidence (0.72 < 0.8 threshold) 
if composite_confidence >= behaviors.validate_confidence_limit:
    # Skip validation - trust detection
    pass
else:
    # Validate decoded text
    if not is_valid_text(text, profile):
        raise TextValidationFailure(...)
```

## Benefits

1. **Data-Driven Decisions**: Replace arbitrary `AsNeeded` logic with quantitative scoring
2. **Performance Optimization**: Skip expensive operations when confidence is high
3. **Robustness**: Multiple candidates provide fallback options
4. **Configurable Risk**: Different thresholds for different validation types
5. **Extensible**: Foundation for future multi-backend detector support

## Default Configuration

Based on discussion:
- **trial_decode_confidence_limit**: 0.7 (moderately aggressive)
- **validate_confidence_limit**: 0.8 (more conservative)  
- **mimetype_confidence_size_constant**: 1024 bytes for full confidence

These defaults balance performance (avoiding unnecessary work) with accuracy (validating uncertain detections).

## Implementation Priority

The confidence system is planned for completion before v2.0 release to provide robust `AsNeeded` behavior. This will be implemented after the current decode system work is complete and before updating the test suite and documentation.

## Future Extensions

- **Multiple detector backends** with precedence ordering
- **Machine learning confidence models** for specialized domains
- **Confidence-based caching** for expensive operations
- **Confidence reporting** in public API for transparency