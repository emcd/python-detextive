# Charset Detector Evaluation Results

**Date**: 2025-11-12
**Detectors tested**: chardet 5.2.0 vs charset-normalizer 3.4.4

## Executive Summary

Both detectors have strengths and weaknesses:
- **charset-normalizer** is better at UTF-8 detection (fewer false positives)
- **chardet** is better at 8-bit encodings (Latin-1, Windows-1252)
- **Overall accuracy**: Tied at 65% on ground-truth tests
- **Performance**: chardet is generally faster (19 vs 4 wins in speed tests)

**Recommendation**: Treat this as detector-behavior reference data. For decode
selection, prefer deterministic trial ordering plus textual validation rather
than complex detector arbitration.

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

### Practical Strategy

1. Keep detector results as hints, not authoritative truth.
2. Use straightforward trial order in decode.
3. Validate decoded text to reject non-textual output.
4. Use HTTP charset when explicitly provided and decodable.

### Detector Choice Guidance

If a single detector is preferred, **chardet remains a reasonable default**:
- More consistent behavior across encoding types
- Better confidence scores
- Faster performance
- Compensate for UTF-8 misses with trial order and text validation.

## Test Scripts

All test scripts available in `.auxiliary/scribbles/`:
- `compare-charset-detectors.py` - General comparison
- `test-normalization-behavior.py` - Standard vs obscure encodings
- `test-decode-accuracy.py` - Ground truth accuracy testing

Run with: `hatch --env develop run python .auxiliary/scribbles/<script>.py`
