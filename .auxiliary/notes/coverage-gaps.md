# Coverage Gap Analysis

Analysis of test coverage gaps identified during examples documentation review. These areas have lower test coverage and should be addressed through the pytest suite rather than documentation examples.

## Coverage Summary

Based on coverage report from 2025-09-12 15:37:

- **Overall coverage**: 65% (386/596 lines)
- **Modules with significant gaps**: charsets.py (48%), detectors.py (48%), inference.py (48%), exceptions.py (34%)

## Specific Gaps by Module

### exceptions.py (34% coverage)

**Missing coverage areas:**
- Exception initialization with location parameters
- Exception message formatting for different scenarios
- Exception chaining and context preservation
- Specific exception subclasses: `CharsetInferFailure`, `ContentDecodeImpossibility`, `MimetypeInferFailure`, `TextInvalidity`, `TextualMimetypeInvalidity`

**Recommended test cases:**
- Test each exception type with and without location parameter
- Verify proper message formatting includes location when provided
- Test exception chaining from underlying library failures
- Test edge cases in exception construction (empty strings, special characters in locations)
- Create a test content patterns module with standardized malformed/edge case content to avoid file I/O during testing

### charsets.py (48% coverage)

**Missing coverage areas:**
- `attempt_decodes()` function edge cases
- `discover_os_charset_default()` functionality
- `trial_decode_as_confident()` with various confidence thresholds
- Character set promotion behavior (ASCII → UTF-8)
- Trial decode failure scenarios

**Recommended test cases:**
- Test `attempt_decodes()` with malformed content and various charsets
- Test OS charset detection on different platforms/environments
- Test trial decode confidence calculation with various content lengths
- Test charset promotion mapping functionality
- Test trial decode with insufficient content quantity

### detectors.py (48% coverage)

**Missing coverage areas:**
- Edge cases in confidence calculation
- Detection with various `Behaviors` configurations
- Error handling paths in detection functions
- Internal logic paths accessible through public API variations

**Recommended test cases:**
- Test detection with custom `Behaviors` configurations to exercise internal confirmation logic
- Test confidence calculation edge cases (very short content, very long content)
- Test detection failures with malformed or ambiguous content
- Use dependency injection patterns with public functions to cover internal function paths without direct testing
- Test MIME type inference scenarios that trigger charset-based detection internally

### inference.py (48% coverage)

**Missing coverage areas:**
- `infer_charset()` and `infer_charset_confidence()` edge cases
- `parse_http_content_type()` with malformed headers
- Complex HTTP Content-Type parsing scenarios
- Internal behavior determination logic accessible through public API

**Recommended test cases:**
- Test HTTP Content-Type parsing with malformed headers (missing semicolons, invalid charset values)
- Test charset inference with conflicting indicators (HTTP header vs content detection)
- Use parameterized tests with different `BehaviorTristate` values on public inference functions to cover internal `_determine_parse_detect()` logic
- Test edge cases in parameter parsing (quoted values, multiple parameters)
- Test inference failures and fallback behaviors

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

1. **High Priority**: exceptions.py - critical for proper error handling
2. **High Priority**: charsets.py - core functionality with complex edge cases
3. **Medium Priority**: detectors.py - internal functions need coverage
4. **Medium Priority**: inference.py - HTTP parsing edge cases
5. **Low Priority**: validation.py, lineseparators.py - already well covered

## Testing Strategy Recommendations

1. **Parametrized tests** for exception types with various inputs and different BehaviorTristate configurations
2. **Curated content testing** for charset detection using a test patterns library with known-good and known-bad content samples
3. **Property-based testing** for charset detection behavioral invariants and round-trip verification
4. **Mock-based testing** for OS charset detection to avoid platform dependencies
5. **Edge case testing** for HTTP Content-Type parsing with malformed inputs
6. **Detection pipeline testing** that exercises complete detection workflows with various content types and behaviors

## Implementation Notes

- Focus on edge cases and error conditions not covered by examples
- Create a dedicated test content patterns module (e.g., `tests/patterns.py`) with curated samples: UTF-8 with BOM, Latin-1 with accented characters, malformed UTF-8 sequences, binary data, etc.
- Use pytest fixtures for common test configurations and behaviors
- Use dependency injection through public API parameters rather than directly testing internal functions
- Mock external dependencies where appropriate (OS charset detection)
- Ensure tests cover both success and failure paths for all functions

## Detailed Expansion on Testing Approaches

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