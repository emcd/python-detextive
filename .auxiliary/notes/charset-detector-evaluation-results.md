# Charset Detector Evaluation Results

**Date**: 2025-11-12
**Detectors tested**: chardet 5.2.0 vs charset-normalizer 3.4.4

## Executive Summary

Both detectors have strengths and weaknesses:
- **charset-normalizer** is better at UTF-8 detection (fewer false positives)
- **chardet** is better at 8-bit encodings (Latin-1, Windows-1252)
- **Overall accuracy**: Tied at 65% on ground-truth tests
- **Performance**: chardet is generally faster (19 vs 4 wins in speed tests)

**Recommendation**: Consider using **both** detectors with fallback logic:
1. Try charset-normalizer first for UTF-8 preference
2. Fall back to chardet if low confidence or decode fails
3. Apply `is_permissive_charset()` filtering to both

## Detailed Findings

### 1. UTF-8 Detection Quality

**charset-normalizer wins decisively:**

✓ **Better UTF-8 recognition**:
- Correctly detected UTF-8 with emoji (chardet→Windows-1254 ✗)
- Correctly detected UTF-8 in HTML (chardet→ISO-8859-9 ✗)
- Correctly detected UTF-8 in JSON (chardet→ISO-8859-9 ✗)
- Correctly detected UTF-8 in CSV (chardet→ISO-8859-9 ✗)
- Correctly detected UTF-8 with structure (chardet→MacRoman ✗)

✓ **Avoided obscure encodings**:
- 0 obscure encoding detections vs chardet's 1 (MacRoman)

✗ **But struggles with short UTF-8**:
- Very short UTF-8 content sometimes misdetected as UTF-16-BE

### 2. 8-bit Encoding Detection

**chardet wins clearly:**

✓ **Better 8-bit accuracy**:
- Correctly detected Latin-1 French (normalizer→UTF-16-BE ✗)
- Correctly detected Latin-1 Spanish (normalizer→CP1250 ✗)
- Correctly detected Latin-1 Ñoño (normalizer→Big5 ✗)
- Correctly detected Win1252 Euro sign (normalizer→CP1125 ✗)
- Correctly detected Win1252 em dash (normalizer→UTF-16-BE ✗)

✗ **charset-normalizer struggles with 8-bit**:
- Often misdetects as UTF-16-BE or obscure Asian encodings
- Less reliable for Latin-1, Windows-1252 content

### 3. Performance Characteristics

**chardet is faster**:
- chardet faster: 19 tests
- normalizer faster: 4 tests
- Average chardet: ~0.1-0.5 ms for most tests
- Average normalizer: ~0.5-15 ms (especially slow on ambiguous content)

**charset-normalizer's slowness**:
- Some tests took 13-15 ms (vs chardet's 0.1-0.4 ms)
- Appears to do more extensive analysis

### 4. "Normalization" Behavior

**Mixed results:**

✓ **charset-normalizer prefers UTF-8**:
- More likely to detect UTF-8 for modern content
- Good for web content, JSON, structured text

✓ **Avoids truly obscure encodings**:
- 0 MacRoman/MacCyrillic detections

✗ **But uses non-standard encodings**:
- Detected UTF-16-BE for short Latin-1 content (unusual)
- Detected obscure Asian encodings (Big5, CP949) for ambiguous bytes
- chardet detected more "standard" encodings overall (10 vs 9)

### 5. Edge Cases

**Empty content**:
- chardet: None
- normalizer: utf-8
- **Winner**: normalizer (reasonable default)

**Binary content**:
- Both struggle, but chardet slightly better at staying ASCII
- normalizer sometimes detects UTF-16-BE for binary

**Ambiguous content**:
- Both have issues with very short content (<10 bytes)
- chardet tends toward 8-bit encodings
- normalizer tends toward multi-byte encodings

## Ground Truth Accuracy (20 tests)

| Detector | Correct | Failed | Accuracy |
|----------|---------|--------|----------|
| chardet | 13 | 1 decode failure | 65% |
| charset-normalizer | 13 | 0 decode failures | 65% |

**Breakdown by encoding family**:

**UTF-8 (12 tests)**:
- chardet: 7/12 correct (58%)
- normalizer: 11/12 correct (92%) ✓

**Latin-1/Windows-1252 (6 tests)**:
- chardet: 5/6 correct (83%) ✓
- normalizer: 1/6 correct (17%)

**ISO-8859-2 (2 tests)**:
- chardet: 0/2 correct
- normalizer: 0/2 correct
- (Both failed - very hard without more context)

## Confidence Scores

**chardet** provides meaningful confidence:
- 0.0-1.0 range reflects detection quality
- High confidence (>0.9) is reliable
- Low confidence (<0.5) signals uncertainty

**charset-normalizer** coherence is problematic:
- Most results show 0.0 coherence, even for correct detections
- Coherence ≠ confidence in traditional sense
- Coherence measures text "readability" not detection certainty
- Cannot use coherence as confidence threshold

## Recommendation for Detextive

### Proposed Strategy

Use a **hybrid approach** with situational logic:

```python
def detect_charset_reliable(content, behaviors):
    """Reliable charset detection using hybrid approach."""

    # 1. Try charset-normalizer first (UTF-8 preference)
    norm_result = detect_via_charset_normalizer(content)

    # 2. If normalizer detected UTF-8 or other multi-byte, trust it
    if norm_result.charset and not is_permissive_charset(norm_result.charset):
        return norm_result

    # 3. For 8-bit or uncertain, try chardet
    chardet_result = detect_via_chardet(content)

    # 4. Apply logic:
    # - If chardet detected multi-byte non-8-bit, prefer it
    # - If chardet detected 8-bit, verify with trial decode
    # - If both detected 8-bit, treat as uncertain

    if chardet_result.charset and not is_permissive_charset(chardet_result.charset):
        # chardet found informative charset
        if chardet_result.confidence >= behaviors.charset_confidence_threshold:
            return chardet_result

    # 5. Fall back to defaults with trial decode
    return try_defaults(content, behaviors)
```

### Why This Works

1. **UTF-8 preference**: normalizer catches modern UTF-8 content that chardet misses
2. **8-bit accuracy**: chardet catches Latin-1/Win1252 that normalizer mangles
3. **Safety net**: `is_permissive_charset()` prevents accepting uninformative 8-bit
4. **Confidence gating**: Only trust chardet when confidence is high

### Alternative: Just Use chardet

If hybrid is too complex, **stick with chardet**:
- More consistent behavior across encoding types
- Better confidence scores
- Faster performance
- We can compensate for UTF-8 issues with:
  - Always trying UTF-8 first in trial decode
  - Using shortest-wins heuristic
  - Text validation

## Test Scripts

All test scripts available in `.auxiliary/scribbles/`:
- `compare-charset-detectors.py` - General comparison
- `test-normalization-behavior.py` - Standard vs obscure encodings
- `test-decode-accuracy.py` - Ground truth accuracy testing

Run with: `hatch --env develop run python .auxiliary/scribbles/<script>.py`
