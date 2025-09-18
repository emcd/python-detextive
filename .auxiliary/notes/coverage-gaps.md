# Coverage Gaps Analysis - Current Status

**Current Coverage: 84% (489/550 lines, 151/208 branches)**
**Previous Coverage: 68%**
**Improvement: +16 percentage points**
**Target: 100%**
**Remaining: 61 uncovered lines, 57 uncovered branches**

## Progress Summary

✅ **Priority 1 (CRITICAL) - COMPLETED**:
- detectors.py default return behavior (lines 97-101, 149-155) ✅
- exceptions.py location parameters (lines 45-48, 56-59, 67-70, 95-98) ✅
- decoders.py exception fallback paths (lines 69-74) ✅

✅ **Priority 2 (HIGH) - COMPLETED**:
- charsets.py codec edge cases (lines 60, 62, 65-67, 117) ✅
- inference.py enhanced inference functions (lines 52-60, 73-95) ✅

✅ **Priority 3 (MEDIUM) - COMPLETED**:
- validation.py edge case (line 193) ✅
- lineseparators.py edge cases (lines 56, 87-88) ✅
- mimetypes.py edge case (line 66) ✅

✅ **Modules Reaching High Coverage**:
- `mimetypes.py`: **100%** (12/12 lines)
- `validation.py`: **97%** (54/54 lines)
- `charsets.py`: **96%** (48/49 lines)
- `lineseparators.py`: **94%** (44/44 lines)
- `decoders.py`: **88%** (28/30 lines)
- `inference.py`: **86%** (82/88 lines)

---

## Remaining Gaps Analysis

### Primary Target: detectors.py (38 uncovered lines, 67% coverage)

**Major Uncovered Functional Areas:**

#### 1. Enhanced Charset Detection with MIME Type Context (Lines 103-110)
```python
# In _detect_charset_confidence function
if __.is_absent( mimetype ): return result                    # Line 103 ❌
if not _mimetypes.is_textual_mimetype( mimetype ): return result # Line 104 ❌
result = _charsets.trial_decode_as_confident(                 # Lines 105-109 ❌
    content, behaviors = behaviors, supplement = supplement, location = location )
return _normalize_charset_detection( content, behaviors, result ) # Line 110 ❌
```

**Function**: Enhanced charset detection that leverages MIME type information
**To Cover**:
- Pass `mimetype` parameter to charset detection
- Test with textual MIME types (text/plain, text/html, etc.)
- Test trial decoding and charset normalization pipeline

#### 2. MIME Type from Charset Validation Pipeline (Lines 214-231)
```python
# In _detect_mimetype_from_charset function
try:
    text, charset_result = _charsets.attempt_decodes(...)     # Lines 217-219 ❌
except _exceptions.ContentDecodeFailure:                      # Line 220 ❌
    if should_error: raise error from None                    # Line 221 ❌
    return result_default                                     # Line 222 ❌
match behaviors.text_validate:                               # Line 223 ❌
    case _BehaviorTristate.Never:                            # Line 224 ❌
        if should_error: raise error                         # Line 225 ❌
        return result_default                                # Line 226 ❌
if not _validation.PROFILE_TEXTUAL( text ):                 # Line 228 ❌
    if should_error: raise error                             # Line 229 ❌
    return result_default                                    # Line 230 ❌
return _MimetypeResult(...)                                  # Line 231 ❌
```

**Function**: Validates decoded text and determines MIME type based on charset
**To Cover**:
- Content decode failures with error/default behaviors
- Text validation behaviors (`text_validate = Never`)
- Non-textual content validation failures
- Error vs default return logic

#### 3. Advanced Detection Functions (Lines 250-256, 278-284)
```python
# Platform-specific magic detection and HTTP parsing
def _detect_via_puremagic(...):                             # Lines 250-256 ❌
def _validate_http_content_type(...):                       # Lines 278-284 ❌
```

**Function**: Platform-specific detection and HTTP Content-Type parsing
**To Cover**:
- Alternative magic detection implementations
- HTTP Content-Type header validation and parsing
- Malformed header handling

#### 4. Edge Case Paths (Lines 185, 194-195, 239, 265, 267)
**Function**: Various edge cases in detection pipeline
**To Cover**:
- Specific error conditions and fallback scenarios
- Content validation edge cases
- Registry and detector failure scenarios

---

### Secondary Target: exceptions.py (13 uncovered lines, 72% coverage)

#### 1. ContentDecodeImpossibility Exception (Lines 67-70)
```python
class ContentDecodeImpossibility( Omnierror, TypeError, ValueError ):
    def __init__(self, location: __.Absential[ _nomina.Location ] = __.absent ) -> None:
        message = "Could not decode probable non-textual content"       # Line 67 ❌
        if not __.is_absent( location ):                               # Line 68 ❌
            message = f"{message} at '{location}'"                     # Line 69 ❌
        super( ).__init__( f"{message}." )                            # Line 70 ❌
```

**Function**: Exception for non-textual content decode attempts
**To Cover**: Trigger this exception with/without location parameter

#### 2. Advanced Exception Scenarios (Lines 106-109, 120, 131-134)
**Function**: Complex exception handling and chaining
**To Cover**:
- Exception chaining scenarios
- Context-specific exception construction
- Advanced error handling paths

---

### Tertiary Targets: Remaining Modules

#### inference.py (6 uncovered lines, 86% coverage)
- Lines 85-87: HTTP Content-Type validation edge cases
- Lines 194-198: Advanced inference edge cases
- Lines 174, 176, 226, 228: Specific inference scenarios

#### decoders.py (2 uncovered lines, 88% coverage)
- Lines 91, 95: Advanced decode edge cases and validation

---

## Implementation Strategy for 100% Coverage

### Phase 1: Enhanced Charset Detection (Lines 103-110)
**Target**: 5-7% coverage increase
```python
def test_charset_detection_with_mimetype_context():
    """Test enhanced charset detection using MIME type information"""
    behaviors = detextive.Behaviors(charset_detect = detextive.BehaviorTristate.Always)
    content = b'Hello, world!'
    result = detextive.detect_charset_confidence(
        content, behaviors=behaviors, mimetype='text/plain')
    # This should trigger the enhanced detection path
```

### Phase 2: MIME Type Validation Pipeline (Lines 214-231)
**Target**: 8-10% coverage increase
```python
def test_mimetype_from_charset_validation():
    """Test MIME type determination with text validation"""
    # Test decode failures
    # Test text validation disabled
    # Test non-textual content validation
    # Test error vs default behaviors
```

### Phase 3: Platform-Specific Detection (Lines 250-256, 278-284)
**Target**: 3-5% coverage increase
```python
def test_puremagic_detection():
    """Test alternative magic detection implementation"""

def test_http_content_type_parsing():
    """Test HTTP Content-Type header parsing edge cases"""
```

### Phase 4: Exception Scenarios (Lines 67-70, 106-109, etc.)
**Target**: 2-3% coverage increase
```python
def test_content_decode_impossibility():
    """Test non-textual content decode exception"""

def test_advanced_exception_scenarios():
    """Test complex exception chaining and context"""
```

### Phase 5: Edge Cases and Branch Coverage
**Target**: Remaining 2-5% to reach 100%
- Focus on uncovered branches
- Error condition edge cases
- Platform-specific code paths

## Specific Implementation Notes

### Critical Paths for 100% Coverage

1. **Enhanced Detection Pipeline**:
   - Requires understanding of how `mimetype` parameter affects charset detection
   - Need tests that exercise trial decoding and normalization
   - Must test interaction between charset and MIME type detection

2. **Text Validation Integration**:
   - Need to understand when `_detect_mimetype_from_charset` is called
   - Must test various `text_validate` behavior settings
   - Need content that fails textual validation

3. **Platform Detection Variants**:
   - Research `puremagic` vs `magic` library differences
   - Create test scenarios for platform-specific detection
   - Test HTTP Content-Type parsing edge cases

4. **Exception Triggering**:
   - Need scenarios that trigger `ContentDecodeImpossibility`
   - Must understand when this exception vs others is raised
   - Test with various content types and configurations

### Testing Strategy Recommendations

1. **Start with detectors.py enhancement paths** (biggest coverage impact)
2. **Use dependency injection** through public API parameters
3. **Create specific test content** designed to trigger uncovered paths
4. **Test behavior configuration combinations** systematically
5. **Mock platform-specific dependencies** where needed

### Estimated Coverage Targets by Phase

- **Phase 1**: 84% → 89% (+5%)
- **Phase 2**: 89% → 95% (+6%)
- **Phase 3**: 95% → 98% (+3%)
- **Phase 4**: 98% → 99% (+1%)
- **Phase 5**: 99% → 100% (+1%)

## Next Actions

1. **Immediate**: Focus on detectors.py lines 103-110 (enhanced charset detection)
2. **Short-term**: Implement MIME type validation pipeline tests (lines 214-231)
3. **Medium-term**: Research and test platform-specific detection functions
4. **Final push**: Exception scenarios and branch coverage refinement

The foundation established by our Priority 1-3 implementation provides an excellent base for reaching 100% coverage. The remaining gaps are primarily in advanced detection scenarios and edge cases rather than core functionality.