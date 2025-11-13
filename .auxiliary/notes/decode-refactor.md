# Decode Function Refactor

## Problem Statement

The current `decode()` implementation has become overly complex with multiple special cases, three different `trial_codecs` usage patterns, and platform-specific encoding issues. The Windows Python 3.11+ doctest failures revealed fundamental issues with how we handle charset detection and validation.

## Core Insight: 8-bit Charsets Are Uninformative

**Key realization**: 8-bit character sets (cp1252, iso-8859-*, etc.) accept any byte sequence because they have one-to-one correspondence between byte values and code points. Trial decodes with these charsets tell us nothing about correctness.

Only **7-bit** (ASCII) and **multi-byte** (UTF-8, Shift-JIS, etc.) charsets provide informative feedback through decode success/failure.

## Design Principles

1. **Ignore MIME type in `decode()`** - Focus solely on getting correct text
2. **Consider confidence for non-8-bit detections** - Even multi-byte charsets can be misdetected; 7-bit (ASCII) especially unreliable
3. **Distrust 8-bit detections** - They always succeed but may produce mojibake
4. **Respect configurable validation behavior** - Honor existing `text_validate` settings
5. **Shortest string wins for multi-byte** - Mojibake produces longer strings
6. **User supplement gets priority among 8-bit** - Respect user knowledge

## New Architecture

### Helper Function: `is_permissive_charset()`

```python
# Module-level cache (always on)
_PERMISSIVE_CHARSET_CACHE: dict[str, bool] = {}

def is_permissive_charset(charset: str) -> bool:
    """Check if charset accepts all byte sequences (8-bit encoding).

    Returns True for: cp1252, iso-8859-*, koi8-r, etc.
    Returns False for: utf-8, ascii, shift-jis, etc.

    Tests both ascending and descending byte sequences to detect
    multi-byte sequence introducers, and checks decoded length
    to ensure 1:1 byte-to-character mapping.
    """
    # Normalize and check cache
    charset_normalized = normalize_charset(charset)
    if charset_normalized in _PERMISSIVE_CHARSET_CACHE:
        return _PERMISSIVE_CHARSET_CACHE[charset_normalized]

    try:
        # Test ascending sequence
        ascending = bytes(range(256))
        text_asc = ascending.decode(charset, errors='strict')

        # Test descending sequence (catches multi-byte introducers)
        descending = bytes(range(255, -1, -1))
        text_desc = descending.decode(charset, errors='strict')

        # Check lengths: must be exactly 256 chars (1:1 mapping)
        is_permissive = (len(text_asc) == 256 and len(text_desc) == 256)

        _PERMISSIVE_CHARSET_CACHE[charset_normalized] = is_permissive
        return is_permissive

    except (UnicodeDecodeError, LookupError):
        # Some bytes failed → informative charset
        _PERMISSIVE_CHARSET_CACHE[charset_normalized] = False
        return False
```

**Implementation notes:**
- Cache always enabled (minimal memory footprint)
- Tests both ascending and descending byte sequences
- Checks decoded length to detect multi-byte encodings
- Handles unknown/future charsets automatically

### New Function: `detect_charset_reliable()`

Wrapper around `detect_charset_confidence()` that validates suspicious detections via trial decode:

```python
def detect_charset_reliable(content, ...):
    """Detect charset with validation of suspicious results.

    Part of public API. Applications can use this for more reliable
    detection than raw detect_charset().
    """
    result = detect_charset_confidence(content, ...)
    detected, confidence = result.charset, result.confidence

    # Consider confidence, especially for 7-bit and multi-byte
    # Even non-8-bit charsets can be misdetected
    if not is_permissive_charset(detected):
        # If confidence is high enough, trust it
        # Reuse existing threshold from behaviors DTO
        if confidence >= behaviors.charset_confidence_threshold:
            return result
        # Otherwise, try defaults as well

    # Detected is 8-bit or low-confidence, try defaults
    python_default = sys.getdefaultencoding()  # utf-8
    os_default = discover_os_charset_default()  # varies

    for default in [python_default, os_default]:
        if not is_permissive_charset(default):
            try:
                content.decode(default)
                # Return with appropriate confidence
                return CharsetResult(charset=default, confidence=...)
            except UnicodeDecodeError:
                continue

    # All informative charsets failed, return original detection
    return result
```

**Note**: Also add `detect_charset_confidence_reliable()` variant that returns full result object.

### Helper Function: `_decode_with_http_content_type()`

Extract HTTP Content-Type handling into helper:

```python
def _decode_with_http_content_type(
    content, http_content_type, behaviors, profile, location
):
    """Attempt decode with charset from HTTP Content-Type header.

    Returns decoded text if successful, None if should fall back to detection.
    Always falls back (never raises) on failure.
    """
    charset = parse_charset_from_content_type(http_content_type)
    if not charset or is_absent(charset):
        return None

    # Use existing trial decode helpers
    try:
        text, result = attempt_decodes(
            content,
            behaviors=behaviors,
            inference=charset,
            location=location
        )
        # Validate if configured
        if should_validate_text(behaviors, result.confidence):
            if not profile(text):
                return None  # Fall back
        return text
    except ContentDecodeFailure:
        return None  # Fall back
```

### Refactored `decode()` Flow

```python
def decode(content, http_content_type=None, charset_supplement=None,
           behaviors=..., profile=..., location=...):
    """Decode bytes to text with intelligent charset selection."""

    if content == b'':
        return ''

    # 1. Try authoritative charset from HTTP Content-Type
    if http_content_type:
        text = _decode_with_http_content_type(
            content, http_content_type, behaviors, profile, location)
        if text is not None:
            return text
        # Fall back to detection

    # 2. Detect charset with validation
    result = detect_charset_confidence_reliable(
        content, behaviors=behaviors, supplement=charset_supplement)
    detected = result.charset

    # 3. Build candidate lists - reuse existing trial decode helpers
    # Use attempt_decodes() and related functions rather than
    # reinventing the wheel

    trial_candidates = []  # Non-8-bit charsets
    actual_candidates = []  # 8-bit charsets

    # Add detected
    if not is_permissive_charset(detected):
        trial_candidates.append(detected)
    else:
        actual_candidates.append(detected)

    # Add defaults if different from detected and non-8-bit
    python_default = sys.getdefaultencoding()  # utf-8
    os_default = discover_os_charset_default()  # varies

    for default in [python_default, os_default]:
        if (default not in trial_candidates
            and default not in actual_candidates
            and not is_permissive_charset(default)):
            trial_candidates.append(default)

    # Add supplement
    if not is_absent(charset_supplement):
        if is_permissive_charset(charset_supplement):
            actual_candidates.insert(0, charset_supplement)
        else:
            trial_candidates.append(charset_supplement)

    # 4. Try candidates using existing helpers
    # Validation timing respects behaviors.text_validate configuration
    text = _try_decode_candidates(
        content, trial_candidates, actual_candidates,
        behaviors, profile, location)

    if text is not None:
        return text

    # 5. No valid decode found
    raise ContentDecodeFailure(location=location)
```

**Implementation notes:**
- Reuse existing `attempt_decodes()` and codec trial functions
- Respect `behaviors.text_validate` configuration (Never/AsNeeded/Always)
- Extract helpers to avoid monolithic decode function

### Decision Priority

When multiple decodes succeed:

1. **Shortest string always wins** (less mojibake)
2. **Tie-breaker**: User supplement over other charsets (user knowledge)
3. **Secondary tie-breaker**: Non-8-bit over 8-bit (more informative)

**Implementation**:
```python
def _try_decode_candidates(...):
    results = []

    # Try all candidates and collect successful decodes
    for charset in all_candidates:
        try:
            text = content.decode(charset)
            if should_validate and not profile(text):
                continue
            results.append((
                len(text),  # Primary: shortest
                charset != charset_supplement,  # Tie-break: supplement wins
                is_permissive_charset(charset),  # Secondary: non-8-bit wins
                charset,
                text
            ))
        except UnicodeDecodeError:
            continue

    if results:
        # Sort by tuple: shortest, then supplement, then non-8-bit
        results.sort()
        return results[0][4]  # Return text

    return None
```

### Validation Timing

Text validation timing is **configurable** via `behaviors.text_validate`:
- **Never**: Skip validation entirely
- **AsNeeded**: Validate based on confidence threshold
- **Always**: Always validate

The existing behavior configuration is preserved. Validation can happen during candidate selection or after - the difference is minimal in practice since validation is already configurable.

## OS Default vs Python Default

- **Python default**: `sys.getdefaultencoding()` → always UTF-8 in Python 3
  - Can be overridden via `PYTHONIOENCODING` or CLI flag
- **OS default**: `locale.getencoding()` (3.11+) or `sys.getfilesystemencoding()`
  - cp1252 on Windows, UTF-8 on modern Linux/Mac

**Strategy**: Try both when they differ, preferring Python default first.

**Special case**: Don't trial decode with cp1252 even if it's OS default (8-bit uninformative).

## Impact on Existing APIs

### `detect_charset()`
- **No change** - Returns raw detector output
- Used when applications just want to know what chardet/charset-normalizer says

### `detect_charset_reliable()` (new)
- Validates suspicious (8-bit) or low-confidence detections
- **Part of public API** along with `detect_charset_confidence_reliable()`
- Used internally by `decode()`

### `decode()`
- **Major refactor** - New candidate selection logic
- Ignores MIME type entirely
- Uses helper functions to avoid monolithic implementation
- Reuses existing trial decode functions
- HTTP Content-Type: always falls back to detection on failure (not configurable)

### `infer_*()` functions
- Minor updates may be needed later (defer for now)
- HTTP Content-Type with charset: trial decode only with specified charset

### `trial_codecs` behavior parameter
- **Deprecated** - Document as ignored
- Keep in API for compatibility but don't use
- New situational logic replaces fixed codec lists

## Charset-Normalizer Investigation

Before implementing, test `charset-normalizer` vs `chardet`:

1. Compare on wide variety of byte patterns
2. Verify it "normalizes" to useful/standard encodings
3. Measure performance characteristics
4. Document findings

`charset-normalizer` is already in dev environment.

## Related Issues

### Windows Python 3.11+ Doctest Failure

Current failure:
```
Expected: 'Café ★'
Got: 'CafÃ© â˜…'
```

Our code is producing UTF-8-as-cp1252 mojibake on Windows. The refactor should fix this by:
1. Detecting UTF-8 via `detect_charset_reliable()`
2. Trying UTF-8 (non-8-bit informative charset)
3. Successfully decoding and validating

### Three Trial Codecs Usage Patterns

Previously documented patterns become:
1. **Opportunistic Decoding** → New `decode()` logic
2. **Authoritative Validation** → HTTP Content-Type handling
3. **Detection Confirmation** → `detect_charset_reliable()`

The fixed lists are replaced by situational logic based on charset properties.

## Implementation Plan

1. Implement and test `is_permissive_charset()` with caching
2. Implement `detect_charset_reliable()`
3. Refactor `decode()` with new candidate selection
4. Update documentation to deprecate `trial_codecs`
5. Test charset-normalizer vs chardet
6. Verify Windows Python 3.11+ doctests pass
7. Update architecture documentation

## Resolved Design Questions

1. **Authoritative charset failure**: Always fall back to detection (not configurable). Users who want exceptions can parse the header themselves and call `.decode()` directly.
2. **`detect_charset_reliable()` public API**: Yes, add both `detect_charset_reliable()` and `detect_charset_confidence_reliable()` to public API.
3. **`infer_*()` functions refactoring**: Defer for later; minor updates may be needed but not part of this refactor.
4. **Validation timing**: Respect existing `behaviors.text_validate` configuration; difference between during/after selection is minimal.
5. **Trust non-8-bit detections**: No, must consider confidence levels. Even multi-byte charsets can be misdetected; 7-bit (ASCII) is especially unreliable.
6. **Reuse existing functions**: Yes, use `attempt_decodes()` and existing trial decode helpers rather than reimplementing.

## All Design Questions Resolved

1. **Confidence threshold**: Use existing `behaviors.charset_confidence_threshold` from DTO
2. **Permissive charset caching**: Always enabled (no flag needed, minimal memory)
3. **Candidate prioritization**: Shortest always wins, user supplement is tie-breaker
4. **Multi-byte detection**: Test both ascending and descending byte sequences, check decoded length == 256
