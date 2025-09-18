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
Test Plan: Version 2.0 Complete Test Suite
*******************************************************************************

Coverage Analysis Summary
===============================================================================

**Current Coverage Status:**
- Overall coverage: 68% (519/758 lines)
- Target coverage: 100%

**Critical Coverage Gaps:**
- **detectors.py**: 48% coverage - CRITICAL gaps in default return behavior (lines 97-101, 149-155)
- **exceptions.py**: 44% coverage - Missing location parameter handling
- **decoders.py**: 75% coverage - New default parameter paths untested
- **inference.py**: 60% coverage - Enhanced inference functions need coverage

**Windows Compatibility Considerations:**
- python-magic vs python-magic-bin MIME type detection differences
- Cross-platform line separator handling
- Cygwin buffer issue mitigations

COVERAGE GAPS PRIORITY
===============================================================================

**CRITICAL: Focus on missing coverage first, comprehensive testing second.**

Test philosophy: Use doctests for examples and happy paths, pytest for coverage gaps and edge cases only.

**Immediate Priority - Uncovered Lines:**

1. **detectors.py lines 97-101, 149-155** - Default return behavior (0% coverage)
2. **exceptions.py lines 45-48, 56-59, 67-70, 95-98, 106-109** - Location parameters
3. **charsets.py lines 60, 62, 65-67, 117** - Codec edge cases
4. **decoders.py lines 69-74** - New default parameter paths
5. **inference.py lines 52-60, 73-95** - Enhanced inference functions

**Secondary Priority - Branch Coverage:**
- Missing branch conditions in location parameter handling
- Trial decode failure edge cases
- Registry detector failure fallback chains

Test Strategy Overview
===============================================================================

**Coverage-Gap-First Approach:**
- Target specific uncovered lines identified in coverage analysis
- Replace existing commented-out tests with minimal effective coverage
- Focus on default return behavior patterns (DetectFailureActions enum)
- Essential edge cases and error paths only
- Avoid comprehensive testing that duplicates doctest coverage

**Test Module Organization:**
- ``test_100_nomina``: Type aliases and common types (minimal - may skip)
- ``test_110_exceptions``: Exception hierarchy and location parameter handling
- ``test_120_core``: Core types, enums, and behaviors
- ``test_200_lineseparators``: Line separator detection and normalization
- ``test_210_mimetypes``: MIME type utility functions
- ``test_220_charsets``: Charset detection utilities and codec handling
- ``test_300_validation``: Text validation and reasonableness checking
- ``test_310_detectors``: Core detection functions (highest priority)
- ``test_400_inference``: Context-aware inference functions
- ``test_500_decoders``: High-level decoding and integration functions

Test Module Specifications
===============================================================================

test_100_nomina (Optional)
-------------------------------------------------------------------------------

**Scope**: Type aliases and common definitions

**Assessment**: Minimal testing needed - type aliases don't require extensive testing.
May skip this module unless coverage tools require it.

**Basic Tests (000-099)**:
- Import verification
- Type alias accessibility

test_110_exceptions
-------------------------------------------------------------------------------

**Current Coverage**: 72% ✅ - Location parameter gaps resolved

**COVERAGE GAP FOCUS**: Lines 45-48, 56-59, 67-70, 95-98, 106-109 ✅ COMPLETED

**Basic Tests (000-099)**:
- Exception hierarchy verification
- Import and inheritance structure validation

**CharsetDetectFailure Tests (100-119)**:
- Construction with and without location parameter (lines 42-48)
- String location message formatting
- pathlib.Path location handling
- Absential location handling (__.absent)

**CharsetInferFailure Tests (120-139)**:
- Construction with and without location parameter (lines 52-59)
- Location context in inference failure messages

**MimetypeDetectFailure Tests (140-159)**:
- Construction with and without location parameter (lines 61-70)
- Various location types (str, Path) in messages

**ContentDecodeFailure Tests (160-179)**:
- Construction with charset and location details (lines 72-82)
- Exception chaining preservation

**Exception Hierarchy Tests (180-199)**:
- Omniexception base class behavior
- Omnierror inheritance and catching patterns
- Multiple inheritance with built-in exception types
- Package-wide exception catching via Omnierror

**Implementation Notes:**
- Test all exception types with both present and absent location parameters
- Verify proper message formatting includes location when provided
- Test exception chaining with 'from' clauses
- Cross-platform path handling in location parameters

test_120_core
-------------------------------------------------------------------------------

**Current Coverage**: 100% - Maintain coverage while expanding tests

**Basic Tests (000-099)**:
- Module import verification
- Constant value validation (CHARSET_DEFAULT, MIMETYPE_DEFAULT)

**Enum Tests (100-199)**:
- BehaviorTristate enum values and behavior
- CodecSpecifiers enum values and usage
- DetectFailureActions enum values and semantics
- Enum string representations and comparisons

**Behaviors Configuration Tests (200-299)**:
- Default Behaviors instance validation
- Custom Behaviors instance creation
- Field defaults and validation
- Detector order sequence handling
- Tristate behavior configurations

**Result Types Tests (300-399)**:
- CharsetResult construction and field access
- MimetypeResult construction and field access
- Confidence value validation (0.0 to 1.0 range)
- Optional charset handling in CharsetResult

**Confidence Calculation Tests (400-499)**:
- confidence_from_bytes_quantity with various content lengths
- Confidence divisor behavior testing
- Edge cases: empty content, very long content
- Custom behavior configuration effects

**Implementation Notes:**
- Test all enum values and their auto-generated identities
- Test confidence calculation formula and edge cases
- Validate behavior configuration precedence and defaults

test_200_lineseparators
-------------------------------------------------------------------------------

**Current Coverage**: 86% - Good coverage but expand for completeness

**Basic Tests (000-099)**:
- Enum structure and values validation
- Import accessibility verification

**Detection Tests (100-199)**:
- Unix LF detection from byte content
- Windows CRLF detection from byte content
- Classic Mac CR detection from byte content
- Mixed line ending detection (first-wins behavior)
- Empty content detection (returns None)
- Content without line endings (returns None)
- Integer sequence input handling
- Detection limit parameter behavior

**Normalization Tests (200-299)**:
- normalize_universal: all endings to LF conversion
- normalize_universal: content without endings (unchanged)
- normalize_universal: empty content handling
- Individual enum normalize methods (CR, CRLF, LF)
- Preserve content that's already normalized

**Platform Conversion Tests (300-399)**:
- nativize method behavior per platform
- Unix LF to platform-specific conversion
- Edge cases in platform conversion
- Content without line endings in nativize

**Edge Case Tests (400-499)**:
- Very long content with mixed endings
- Consecutive line separators
- Line separators at content boundaries
- Invalid or malformed line ending sequences

**Windows Compatibility Tests (500-599)**:
- CRLF detection accuracy on Windows
- Cross-platform nativize behavior consistency
- Large content handling (Cygwin buffer considerations)

**Implementation Notes:**
- Use content patterns for consistent test data
- Test detection precedence (which separator wins in mixed content)
- Verify immutability of enum instances
- Cross-platform testing considerations for nativize behavior

test_210_mimetypes
-------------------------------------------------------------------------------

**Current Coverage**: 89% - High coverage but complete edge cases

**Basic Tests (000-099)**:
- Module import and function accessibility

**Textual MIME Type Tests (100-199)**:
- is_textual_mimetype with text/* prefixes
- Known textual application types (json, xml, javascript, yaml)
- Textual suffixes (+json, +xml, +yaml, +toml)
- Non-textual types rejection (image/*, video/*, audio/*)
- Empty and malformed MIME type handling
- Case sensitivity in MIME type evaluation

**Edge Case Tests (200-299)**:
- MIME types with parameters (text/plain; charset=utf-8)
- Vendor-specific MIME types (application/vnd.*)
- Custom and unknown MIME types
- Very long MIME type strings
- MIME types with unusual characters

**Implementation Notes:**
- Comprehensive coverage of textual vs non-textual classification
- Test MIME type parameter handling if applicable
- Edge cases for malformed input
- Performance testing with large MIME type lists

test_220_charsets
-------------------------------------------------------------------------------

**Current Coverage**: 81% - Improve to cover codec edge cases

**COVERAGE GAP FOCUS**: Lines 60, 62, 65-67, 117 (codec specifier branches and trial decode failures)

**Basic Tests (000-099)**:
- Module import verification
- Function accessibility validation

**OS Charset Detection Tests (100-199)**:
- discover_os_charset_default function behavior
- Cross-platform charset default handling
- Caching behavior for OS charset detection
- Environment variable influence testing

**Codec Resolution Tests (200-299)**:
- CodecSpecifiers enum handling in attempt_decodes
- OsDefault codec specifier behavior
- PythonDefault codec specifier behavior
- UserSupplement codec specifier behavior
- FromInference codec specifier behavior
- Invalid codec name handling

**Trial Decode Tests (300-399)**:
- attempt_decodes with valid charset inference
- attempt_decodes with malformed content
- attempt_decodes with unsupported charset names
- trial_decode_as_confident function behavior
- Confidence calculation in trial decoding
- Exception handling in decode failures

**Charset Promotion Tests (400-499)**:
- ASCII to UTF-8 promotion behavior
- UTF-8 to UTF-8-sig promotion behavior
- Custom promotion mapping handling
- Promotion precedence and conflict resolution

**Implementation Notes:**
- Mock environment for OS charset testing
- Test all CodecSpecifiers enum variants
- Verify confidence calculation accuracy
- Cross-platform charset handling differences
- Error path testing for decode failures

test_300_validation
-------------------------------------------------------------------------------

**Current Coverage**: 93% - Minimal gaps, focus on edge cases

**Basic Tests (000-099)**:
- Module import and function accessibility

**Text Validation Profile Tests (100-199)**:
- Default profile behavior and validation
- Custom profile creation and application
- Profile parameter validation
- Immutable profile handling

**Text Reasonableness Tests (200-299)**:
- is_valid_text with normal textual content
- is_valid_text with control character heavy content
- is_valid_text with whitespace-only content
- is_valid_text with binary data rejection
- Unicode normalization considerations
- Very long text validation performance

**BOM Handling Tests (300-399)**:
- BOM detection and handling in validation
- UTF-8, UTF-16, UTF-32 BOM recognition
- BOM removal in validation process
- Invalid BOM sequence handling

**Character Ratio Tests (400-499)**:
- Character ratio calculations at boundaries
- Threshold validation for ratio limits
- Edge cases with minimal content
- Ratio calculation with various character sets

**Implementation Notes:**
- Test validation profiles with extreme content
- BOM handling across different Unicode encodings
- Character ratio boundary condition testing
- Performance considerations with large text

test_310_detectors (HIGHEST PRIORITY)
-------------------------------------------------------------------------------

**Current Coverage**: 67% ✅ - Default return behavior gaps resolved

**COVERAGE GAP FOCUS**: Lines 97-101, 149-155 ✅ COMPLETED

**Basic Tests (000-099)**:
- Module import verification
- Registry container initialization
- Detector registration verification

**DEFAULT RETURN BEHAVIOR TESTS (100-199) - CRITICAL**:
- DetectFailureActions.Default returns default with confidence 0.0
- DetectFailureActions.Error raises appropriate exceptions
- charset_on_detect_failure configuration behavior
- mimetype_on_detect_failure configuration behavior
- Mixed failure behaviors (charset defaults, mimetype errors)
- Empty content handling in both failure modes
- Failed detection with various default values

**Charset Detection Tests (200-299)**:
- detect_charset with UTF-8 content
- detect_charset with ASCII content (promotion to UTF-8)
- detect_charset with Latin-1 content
- detect_charset with malformed content
- detect_charset_confidence function behavior
- Empty content handling (returns UTF-8 with confidence 1.0)
- Supplement parameter usage
- Location parameter context

**MIME Type Detection Tests (300-399)**:
- detect_mimetype with magic byte detection
- detect_mimetype with extension fallback
- detect_mimetype_confidence function behavior
- Empty content handling (returns text/plain with confidence 1.0)
- Charset parameter influence on MIME detection
- Binary content detection and classification

**Registry System Tests (400-499)**:
- Detector registration and retrieval
- NotImplemented return handling for missing dependencies
- Detector ordering configuration via Behaviors
- Registry iteration and fallback behavior
- Custom detector registration
- Detector failure and recovery patterns

**Integration Tests (500-599)**:
- Combined charset and MIME type detection workflows
- Context-aware detection with location hints
- Behavior configuration influence on detection
- Error recovery and fallback strategies
- Performance testing with large content

**Windows Compatibility Tests (600-699)**:
- python-magic vs python-magic-bin MIME type differences
- Cross-platform magic byte interpretation
- Cygwin buffer handling for large content
- Platform-specific charset detection differences

**Implementation Notes:**
- CRITICAL: Test all DetectFailureActions enum variants in isolation and combination
- Test default return behavior with various custom default values
- Validate confidence scoring for failure scenarios (must be 0.0)
- Mock detector registry for dependency injection testing
- Cross-platform testing considerations for magic libraries
- Property-based testing for detection determinism

test_400_inference
-------------------------------------------------------------------------------

**Current Coverage**: 60% - Enhanced inference functions need coverage

**COVERAGE GAP FOCUS**: Lines 52-60, 73-95 (enhanced inference with default parameters)

**Basic Tests (000-099)**:
- Module import and function accessibility

**Charset Inference Tests (100-199)**:
- infer_charset with HTTP Content-Type headers
- infer_charset with location extension hints
- infer_charset with charset supplement parameters
- infer_charset_confidence function behavior
- Context priority resolution (HTTP > location > content)
- Default parameter usage in inference

**MIME Type and Charset Inference Tests (200-299)**:
- infer_mimetype_charset combined detection
- infer_mimetype_charset_confidence function behavior
- HTTP Content-Type parsing and validation
- Location-based inference precedence
- Supplement parameter handling
- Default value application

**HTTP Content-Type Parsing Tests (300-399)**:
- Valid Content-Type header parsing
- Malformed Content-Type header handling
- Charset parameter extraction from headers
- MIME type parameter handling
- Case sensitivity in header parsing
- Missing or incomplete headers

**Context Resolution Tests (400-499)**:
- Multiple context source priority handling
- Conflicting context resolution
- Context validation and sanitization
- Context-aware confidence scoring
- Error handling in context processing

**Enhanced Default Behavior Tests (500-599)**:
- Custom charset_default and mimetype_default parameters
- Default behavior with inference failures
- Mixed default and error behaviors
- Context-aware default selection

**Implementation Notes:**
- Test HTTP Content-Type parsing with malformed headers
- Verify context priority: HTTP > location > content analysis
- Test inference with conflicting context indicators
- Default behavior testing with new parameter patterns
- Integration testing with complete inference workflows

test_500_decoders
-------------------------------------------------------------------------------

**Current Coverage**: 88% ✅ - Default parameter path gaps resolved

**COVERAGE GAP FOCUS**: Lines 69-74 ✅ COMPLETED

**Basic Tests (000-099)**:
- Module import and function accessibility

**High-Level Decode Tests (100-199)**:
- decode function with valid content and detection
- decode function with malformed content
- decode function with custom charset_default parameter
- decode function with custom mimetype_default parameter
- decode function with validation profile parameters
- decode function error handling and fallback

**Default Parameter Tests (200-299)**:
- Custom default values in decode function
- Default behavior with detection failures
- Graceful degradation with default parameters
- Validation of default parameter precedence
- Error handling when defaults are insufficient

**Integration Workflow Tests (300-399)**:
- Complete detection → validation → decode pipeline
- HTTP Content-Type integration in decode
- Location context usage in decode
- Supplement parameter propagation
- Behavior configuration effects on decode

**Error Handling Tests (400-499)**:
- ContentDecodeFailure exception scenarios
- Decode error recovery with fallback charsets
- Validation failure handling in decode
- Exception chaining in decode failures
- Location context in error messages

**Performance Tests (500-599)**:
- Large content decoding performance
- Memory usage with large content
- Decode timeout behavior (if applicable)
- Streaming decode considerations

**Implementation Notes:**
- Test new default parameter patterns comprehensively
- Integration testing with complete detection pipeline
- Error path testing with proper exception chaining
- Performance testing with various content sizes
- Validation profile integration testing

Test Data and Patterns
===============================================================================

**Content Patterns Module**: ``tests/test_000_detextive/patterns.py``

Provides curated byte sequences covering:
- Charset detection samples (UTF-8, ASCII, Latin-1, Windows-1252, malformed)
- MIME type detection samples (text, JSON, binary magic bytes)
- Line separator patterns (Unix, Windows, Mac, mixed)
- Content length patterns (empty, minimal, short, long)
- Validation patterns (reasonable text, control characters, binary)
- Error condition patterns (undetectable content, decode failures)
- Windows compatibility patterns (platform-specific detection differences)

**Test Fixtures**:
- Behaviors configurations for various testing scenarios
- Mock detector functions for registry testing
- Cross-platform expected outcomes
- Performance benchmarking baselines

Cross-Platform Testing Strategy
===============================================================================

**Windows Compatibility**:
- python-magic vs python-magic-bin detection differences
- Cygwin buffer handling validation
- Platform-specific line separator handling
- Unicode handling across platforms

**Testing Approach**:
- Platform variant patterns for content with different expected outcomes
- Conditional test expectations based on platform
- Mock detector behavior for consistent cross-platform testing
- Performance considerations for platform-specific libraries

Implementation Priorities - COVERAGE GAPS FIRST
===============================================================================

**Priority 1 (CRITICAL) - COMPLETED ✅**:
- **detectors.py lines 97-101, 149-155**: Default return behavior (test_310_detectors) ✅
- **exceptions.py lines 45-48, 56-59, 67-70, 95-98, 106-109**: Location parameters (test_110_exceptions) ✅
- **decoders.py lines 69-74**: New default parameter paths (test_500_decoders) ✅
- **Coverage improvement**: 68% → 77% (+9 percentage points)

**Priority 2 (HIGH) - Significant Coverage Gaps**:
- **charsets.py lines 60, 62, 65-67, 117**: Codec edge cases (test_220_charsets)
- **inference.py lines 52-60, 73-95**: Enhanced inference functions (test_400_inference)

**Priority 3 (MEDIUM) - Minor Coverage Gaps**:
- **validation.py line 193**: Remaining validation edge case (test_300_validation)
- **lineseparators.py lines 56, 87-88**: Line separator edge cases (test_200_lineseparators)
- **mimetypes.py line 66**: MIME type edge case (test_210_mimetypes)

**Priority 4 (LOW) - Well Covered Modules**:
- **core.py**: Maintain existing 100% coverage (test_120_core)
- **nomina.py**: Already 100% covered (test_100_nomina may be skipped)

**PHILOSOPHY**: Write minimal tests targeting only uncovered lines. Avoid comprehensive testing that duplicates doctest coverage or tests functionality already covered by examples.

Success Metrics
===============================================================================

**Coverage Targets**:
- Overall coverage: 100% (from current 68%)
- detectors.py: 100% (from current 48%) - CRITICAL
- exceptions.py: 100% (from current 44%)
- decoders.py: 100% (from current 75%)
- inference.py: 100% (from current 60%)

**Functional Validation**:
- All DetectFailureActions enum variants tested
- Default return behavior patterns comprehensively covered
- Cross-platform compatibility validated
- Exception handling with location parameters complete
- Integration workflows tested end-to-end

**Quality Assurance**:
- Property-based testing for behavioral invariants
- Performance testing with large content
- Memory usage validation
- Cross-platform test execution success
- Windows-specific compatibility verification

Implementation Notes
===============================================================================

**Dependencies Requiring Injection**:
- OS charset detection for platform testing
- Magic library detection for cross-platform testing
- Registry detector functions for failure scenario testing

**Filesystem Operations**:
- All test content provided via patterns module (no filesystem reads)
- Location context testing with mock paths
- Cross-platform path handling validation

**External Services**:
- No external network testing required
- All magic byte detection with local libraries
- HTTP Content-Type testing with direct header values (no mocking needed)

**Architectural Considerations**:
- Immutable object testing requires constructor-based injection
- Registry testing through public API detector configuration
- Behavior configuration testing via Behaviors dataclass
- Exception testing through expected failure scenarios

**CRITICAL Testing Focus**:
The default return behavior pattern (DetectFailureActions enum) is the most
critical uncovered functionality and must be prioritized for comprehensive
testing to ensure system reliability with the new graceful degradation
capabilities.