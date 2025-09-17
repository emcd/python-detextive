# Coverage Gap Analysis

Analysis of test coverage gaps identified after implementation of default return behavior pattern and related architectural changes. These areas require targeted test development to ensure robustness of the new failure handling capabilities.

## Coverage Summary

Based on coverage report from 2025-09-16 20:04:

- **Overall coverage**: 68% (519/758 lines)
- **Modules with significant gaps**: detectors.py (48%), exceptions.py (44%), inference.py (60%), decoders.py (75%)

### Coverage Improvement Notes
- Overall coverage improved from 65% to 68%
- charsets.py improved significantly to 81% coverage
- New gaps identified in default return behavior patterns

## Specific Gaps by Module

### exceptions.py (44% coverage)

**Missing coverage areas:**
- Exception initialization with location parameters (lines 45-48, 56-59, 67-70, 95-98, 106-109)
- Exception message formatting for different scenarios
- Exception chaining and context preservation
- Branch coverage for location parameter handling (lines 46, 57, 68, 96, 107)
- Exception subclasses with location-specific messaging

**Recommended test cases:**
- Test each exception type with and without location parameter
- Verify proper message formatting includes location when provided
- Test exception chaining from underlying library failures
- Test edge cases in exception construction (empty strings, special characters in locations)
- Test branch conditions in location parameter handling

### charsets.py (81% coverage - Improved)

**Remaining missing coverage areas:**
- Specific codec specifier branches in `attempt_decodes()` (lines 60, 62, 65-67)
- Trial decode failure edge cases (line 117)
- Error handling paths in codec resolution

**Recommended test cases:**
- Test all `CodecSpecifiers` enum variants including `UserSupplement`
- Test `attempt_decodes()` with malformed content causing decode failures
- Test trial decode with unsupported charset names
- Test OS charset detection with mocked environment variations

### detectors.py (48% coverage) - Critical for Default Return Behavior

**Missing coverage areas:**
- **Default return behavior paths** (lines 97-101, 149-155) - NEW CRITICAL GAPS
- Detection failure scenarios with `DetectFailureActions.Default`
- Detection failure scenarios with `DetectFailureActions.Error`
- Empty content edge cases (line 89, 142)
- `_detect_mimetype_from_charset()` function entirely (lines 205-230)
- `_confirm_charset_detection()` edge cases (lines 194-195)
- Registry detector failure fallback chains

**HIGH PRIORITY - Default Return Behavior Test Cases:**
- Test `charset_on_detect_failure = DetectFailureActions.Default` returns default with confidence 0.0
- Test `mimetype_on_detect_failure = DetectFailureActions.Default` returns default with confidence 0.0
- Test `charset_on_detect_failure = DetectFailureActions.Error` raises appropriate exceptions
- Test `mimetype_on_detect_failure = DetectFailureActions.Error` raises appropriate exceptions
- Test empty content handling in both failure modes
- Test failed charset detection with various default values
- Test failed mimetype detection with various default values
- Test mixed failure behaviors (charset defaults, mimetype errors)

**Additional recommended test cases:**
- Test detection with no available detectors (registry empty scenarios)
- Test `_detect_mimetype_from_charset()` with charset-based MIME type inference
- Test confidence calculation edge cases (very short content, very long content)
- Test detection failures with malformed or ambiguous content

### inference.py (60% coverage - Improved)

**Missing coverage areas related to default behavior:**
- Inference functions with new `charset_default` and `mimetype_default` parameters
- HTTP Content-Type parsing edge cases
- Context-aware inference failure scenarios
- Behavior determination logic with new failure handling

**Recommended test cases:**
- Test inference functions with custom default values
- Test HTTP Content-Type parsing with malformed headers
- Test charset inference with conflicting indicators (HTTP header vs content detection)
- Test inference failures with different failure action configurations
- Test combined inference with mixed failure behaviors

### decoders.py (75% coverage - NEW GAPS)

**Missing coverage areas related to default behavior:**
- `decode()` function with new default value parameters (lines 69-74)
- Exception handling with default return behavior enabled
- Fallback logic in `decode()` when detection fails

**Recommended test cases:**
- Test `decode()` with custom `charset_default` and `mimetype_default` values
- Test `decode()` with detection failure scenarios and graceful degradation
- Test exception handling paths when default return behavior is disabled

### validation.py (93% coverage - minimal gaps)

**Missing coverage areas:**
- Edge cases in validation profile application
- BOM handling edge cases
- Character ratio calculations at boundary conditions

**Recommended test cases:**
- Test validation with content exactly at ratio thresholds
- Test BOM handling with various Unicode encodings
- Test validation profiles with edge case character combinations

### lineseparators.py (88% coverage - minimal gaps)

**Missing coverage areas:**
- Edge cases in line separator detection
- Mixed line ending scenarios with unusual combinations

**Recommended test cases:**
- Test detection with unusual line ending combinations
- Test edge cases in content with only separators

## Priority Areas for Test Development

### Critical Priority (Default Return Behavior)
1. **CRITICAL**: detectors.py - Default return behavior paths completely untested
2. **HIGH**: decoders.py - New default parameter paths need coverage
3. **HIGH**: inference.py - Enhanced inference with default values

### High Priority (Core Functionality)
4. **HIGH**: exceptions.py - Exception handling crucial for reliability
5. **MEDIUM**: charsets.py - Improved but codec edge cases remain

### Low Priority (Well Covered)
6. **LOW**: validation.py, lineseparators.py - Already well covered

## Testing Strategy Recommendations

### Priority 1: Default Return Behavior Testing
1. **Failure action configuration testing** - Parametrized tests with `DetectFailureActions.Default` vs `DetectFailureActions.Error`
2. **Default value validation** - Test all functions with custom default parameters
3. **Mixed behavior testing** - Test functions with different failure actions for charset vs mimetype
4. **Confidence scoring validation** - Verify confidence = 0.0 for default returns
5. **Integration testing** - Test complete detection workflows with graceful degradation

### Priority 2: Core Functionality
6. **Exception handling** - Test all exception types with and without location parameters
7. **Charset edge cases** - Test codec specifier variants and error paths
8. **Registry testing** - Test detector registry failure scenarios
9. **HTTP parsing** - Test malformed Content-Type headers
10. **Property-based testing** - Detection invariants and round-trip verification

## Implementation Notes

### Critical Additions for Default Return Behavior
- **Test all DetectFailureActions enum variants** in isolation and combination
- **Test default value parameters** with various custom values and edge cases
- **Validate confidence scoring** for failure scenarios (must be 0.0)
- **Test behavioral consistency** between string-returning and confidence-returning functions

### General Testing Guidance
- Focus on edge cases and error conditions not covered by examples
- Create a dedicated test content patterns module (e.g., `tests/patterns.py`) with curated samples
- Use pytest fixtures for common test configurations and behaviors, especially `Behaviors` with different failure actions
- Use dependency injection through public API parameters rather than directly testing internal functions
- Mock external dependencies where appropriate (OS charset detection)
- Ensure tests cover both success and failure paths for all functions
- **Priority focus**: Test coverage gaps in default return behavior are critical for system reliability

## Detailed Expansion on Testing Approaches

### Default Return Behavior Testing Strategy

The default return behavior pattern requires comprehensive testing to ensure graceful degradation works correctly:

**Failure Scenario Testing:**
```python
# Test charset detection failure with default return
def test_charset_detect_failure_default():
    behaviors = Behaviors(charset_on_detect_failure=DetectFailureActions.Default)
    result = detect_charset_confidence(malformed_content, behaviors=behaviors, default='ascii')
    assert result.charset == 'ascii'
    assert result.confidence == 0.0

# Test charset detection failure with exception
def test_charset_detect_failure_error():
    behaviors = Behaviors(charset_on_detect_failure=DetectFailureActions.Error)
    with pytest.raises(CharsetDetectFailure):
        detect_charset_confidence(malformed_content, behaviors=behaviors)
```

**Mixed Behavior Testing:**
```python
# Test mixed failure behaviors (charset defaults, mimetype errors)
def test_mixed_failure_behaviors():
    behaviors = Behaviors(
        charset_on_detect_failure=DetectFailureActions.Default,
        mimetype_on_detect_failure=DetectFailureActions.Error
    )
    # Should return default charset but raise exception for mimetype
```

**Integration Testing:**
```python
# Test complete pipeline with graceful degradation
def test_decode_with_graceful_degradation():
    behaviors = Behaviors(
        charset_on_detect_failure=DetectFailureActions.Default,
        mimetype_on_detect_failure=DetectFailureActions.Default
    )
    # Test that decode() function handles detection failures gracefully
```

### Curated Content Testing Strategy

Create a comprehensive library of test patterns with known expected outcomes:

- **Known charset samples**: UTF-8, Latin-1, Windows-1252, etc. with predictable detection outcomes
- **Malformed content**: Invalid UTF-8 sequences, truncated multibyte characters
- **Edge cases**: Empty content, content with only whitespace, very short content
- **Ambiguous content**: 7-bit ASCII that could be multiple charsets
- **Binary content**: Images, executables with magic bytes for MIME detection

### Property-Based Testing Strategy

Use hypothesis to test behavioral invariants and properties that should hold regardless of specific input:

**Round-trip testing**: Generate Unicode text, encode with known charset, verify detection recovers the original charset (or acceptable promotion like ASCII → UTF-8):
```python
@given(text=st.text(), charset=st.sampled_from(['utf-8', 'latin1', 'cp1252']))
def test_charset_roundtrip(text, charset):
    encoded = text.encode(charset, errors='ignore')
    detected = detect_charset(encoded)
    assert detected in [charset] + ACCEPTABLE_PROMOTIONS[charset]
```

**Confidence monotonicity**: Verify confidence increases with content length for identical repeated patterns:
```python
@given(pattern=st.text(min_size=1, max_size=20))
def test_confidence_monotonic(pattern):
    short = (pattern * 10).encode('utf-8')
    long = (pattern * 100).encode('utf-8')
    conf_short = detect_charset_confidence(short).confidence
    conf_long = detect_charset_confidence(long).confidence
    assert conf_long >= conf_short
```

**Detection determinism**: Same input always produces same result:
```python
@given(content=st.binary())
def test_detection_deterministic(content):
    result1 = detect_charset(content)
    result2 = detect_charset(content)
    assert result1 == result2
```

**Validation consistency**: Text validation should be consistent with charset detection success:
```python
@given(content=st.binary())
def test_validation_consistency(content):
    charset = detect_charset(content)
    if charset:
        try:
            text = content.decode(charset)
            assert is_valid_text(text) or charset in LEGACY_CHARSETS
        except UnicodeDecodeError:
            pass  # Detection can suggest charset that still fails edge cases
```

This approach tests the logical properties and invariants of detection rather than specific outcomes, which is valuable for catching regression bugs and ensuring behavioral consistency.

### Detection Pipeline Testing

Test complete detection workflows that mirror real-world usage:

- **Content detection workflows**: detect charset → detect MIME type → validate → decode
- **HTTP content processing**: parse Content-Type → infer missing information → validate textuality
- **Error recovery workflows**: failed detection → fallback behaviors → user defaults
- **Configuration scenarios**: custom behaviors affecting entire detection chain
- **Inference workflows**: combined MIME type and charset inference with various content types

This integration testing ensures that components work correctly together and that behavior configurations properly influence the entire pipeline.

**Note on real-world content**: If broader detection coverage is needed, consider extracting content signatures from real-world examples into the curated patterns library, or create a separate slow test suite that examines actual diverse content samples.