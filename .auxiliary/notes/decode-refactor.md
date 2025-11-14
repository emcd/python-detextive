# Decode Function Refactor

## Problem Statement

The current `decode()` implementation has become overly complex with multiple special cases, three different `trial_codecs` usage patterns, and platform-specific encoding issues. The Windows Python 3.11+ doctest failures revealed fundamental issues with how we handle charset detection and validation.

## Core Insight: Charset Detection is Fundamentally Hard

**Key realization**: Without context, charset detection is heuristics all the way down. No amount of algorithmic complexity can solve the fundamental ambiguity problem.

**Examples of inherent ambiguity:**
- UTF-8 Turkish text decoded as ISO-8859-9 produces valid-looking mojibake
- ISO-8859-9 Turkish text decoded as UTF-8 also produces mojibake
- Both are "valid" decodings with different results
- Without external context (user knowledge, file source, HTTP headers), detection is guessing

## Design Philosophy: Simplicity + User Control

After extensive analysis of multi-tier categorization schemes (permissive vs restrictive, multi-byte vs single-byte, etc.), we conclude:

**Better to be simple and honest about limitations than complex and pretending to solve the unsolvable.**

### What We Learned

1. **CP1252 is not fully permissive**: Has 5 undefined bytes (0x81, 0x8d, 0x8f, 0x90, 0x9d)
2. **ISO-8859-* variants are fully permissive**: All 256 bytes decode (many variants exist for different languages)
3. **ASCII compatibility is universal**: All major 8-bit encodings preserve ASCII in bytes 0x00-0x7F
4. **UTF-8 vs CP1252 length heuristic works**: UTF-8 multi-byte always produces shorter strings than 8-bit misinterpretation
5. **But length heuristic fails for other encodings**: Turkish ISO-8859-9 vs UTF-8 can produce same-length mojibake

### Implementation Findings

`is_permissive_charset()` successfully implemented:
```python
def is_permissive_charset(charset: str) -> bool:
    """Check if charset accepts all 256 byte values."""
    # Test ascending and descending sequences
    # Check length == 256 (1:1 byte-to-char mapping)
    # Cache results
```

Results:
- ✅ ISO-8859-1: `True` (fully permissive)
- ✅ CP1252: `False` (5 undefined bytes)
- ✅ ASCII: `False` (only 128 values)
- ✅ UTF-8: `False` (multi-byte sequences)

But this revealed new complexity: need to subcategorize "restrictive" into multi-byte vs single-byte to avoid CP1252 mojibake before UTF-8 attempts.

**This led to a design rabbit hole that misses the forest for the trees.**

## Simplified Design (Current Direction)

### Principles

1. **Put user in control**: Provide supplement as `str` or codec specifier
2. **Use sensible defaults**: OS charset for local files, Python charset (usually UTF-8) for general use
3. **Trust high-confidence detection**: But allow it to be overridden by user/context
4. **Keep it simple**: Fewer tiers, clearer behavior, easier to reason about

### Trial Order Strategy

```python
trial_order = [
    UserSupplement,      # User knows their data (highest priority)
    OsDefault,           # Sensible for local filesystem content
    PythonDefault,       # Usually UTF-8, can be set via PYTHONIOENCODING
]

# Insert detected charset based on confidence:
if detection.confidence >= behaviors.trial_decode_confidence:
    trial_order.insert(1, FromInference)  # After user, before OS
else:
    trial_order.append(FromInference)     # At end (suspicious)
```

### User Supplement Enhancement

Allow `charset_supplement` to be either:
- **`str`**: Specific charset name (e.g., `'utf-8'`, `'iso-8859-9'`)
- **Codec specifier**: `OsDefault`, `PythonDefault`, etc.

**Use cases:**
```python
# Internet/web content - prefer UTF-8
decode(content, charset_supplement='utf-8')

# Local filesystem - use OS charset
decode(content, charset_supplement=OsDefault)

# Known legacy encoding
decode(content, charset_supplement='iso-8859-9')
```

### Optional: Use `is_permissive_charset()` for Filtering

One lightweight use of the permissive check:

```python
# Skip truly permissive charsets if non-permissive options exist
candidates = build_candidate_list()
non_permissive = [c for c in candidates if not is_permissive_charset(c)]
if non_permissive:
    candidates = non_permissive  # Prefer informative attempts
```

This prevents trying ISO-8859-1 when UTF-8 is available, without complex multi-tier logic.

## Current Implementation Status

### Implemented ✅

1. **`is_permissive_charset()`** - Working perfectly with caching
2. **HTTP Content-Type handling** - Extracts and validates charset, falls back gracefully
3. **Separate permissive/restrictive lists** - In `_attempt_decodes()`
4. **BOM handling** - `remove_bom` behavior parameter
5. **Charset deduplication** - Normalized before adding to trial list
6. **Empty content uses default** - Not hardcoded to UTF-8

### Issues Discovered 🔍

1. **Complexity creep**: Permissive vs restrictive revealed need for multi-byte vs single-byte subcategorization
2. **CP1252 vs UTF-8 ordering**: CP1252 is "restrictive" but still produces mojibake before UTF-8
3. **Turkish/Finnish ambiguity**: Historical encodings have legitimate sequences that look like UTF-8 mojibake
4. **No magic bullet**: Algorithmic complexity doesn't solve fundamental ambiguity

### Next Steps 🎯

**Decision point**: Continue with complex categorization OR simplify to user-centric approach?

**Recommendation**: Simplify
- Remove complex permissive/restrictive/multi-byte categorization
- Use simple context-based trial order (User → OS → Python → Detection)
- Keep `is_permissive_charset()` only for optional filtering
- Document limitations honestly
- Empower users with supplement options

## Charset Evaluation Results

Comprehensive testing of `chardet` vs `charset-normalizer`:

**Key findings:**
- charset-normalizer: 92% accurate on UTF-8, 17% on Latin-1/CP1252
- chardet: 58% accurate on UTF-8, 83% on Latin-1/CP1252
- Overall: Both tied at 65% accuracy
- charset-normalizer is slower but better for UTF-8
- chardet is faster and better for legacy 8-bit encodings

**Decision**: Stick with chardet for now, provides good balance.

See: `.auxiliary/notes/charset-detector-evaluation-results.md`

## Related Files

- Implementation: `sources/detextive/decoders.py`, `sources/detextive/charsets.py`
- Evaluations: `.auxiliary/evaluations/compare-charset-detectors.py` (and related)
- Results: `.auxiliary/notes/charset-detector-evaluation-results.md`

## Open Questions

1. Should we simplify back to context-based trial order?
2. Keep or remove permissive/restrictive categorization?
3. How much complexity is justified for marginal accuracy gains?
4. What's the right balance between "smart" and "simple"?

## The Honest Documentation Approach

```python
"""
decode() attempts decoding in context-aware order:
1. User supplement (you know your data best)
2. OS default (sensible for local files)
3. Python default (usually UTF-8)
4. Detected charset (if confidence is high)

Charset detection is heuristic and cannot solve fundamental
ambiguities without context. For best results:
- Provide charset_supplement when encoding is known
- Use http_content_type for web content
- Validate results with is_valid_text()
- Consider confidence scores from detect_charset_confidence()

There is no magic bullet for charset detection. We provide
sensible defaults and give you control over the process.
"""
```

**Complexity should serve users, not obscure limitations.**
