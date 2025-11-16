# Confidence Scoring Strategy

## Overview

This document describes the confidence scoring strategy for detection results in detextive. The core principle is that confidence should reflect **both detection quality AND sample size adequacy**.

## Design Philosophy

### Why Scale All Confidence by Content Size?

1. **Small samples are inherently less reliable**: A charset detection on 10 bytes is fundamentally less trustworthy than the same detection on 1000 bytes, regardless of what the detector reports.

2. **Empirical justification**: `chardet` is known to be overconfident on small samples, sometimes reporting high confidence on minimal data that could be interpreted multiple ways.

3. **Cost-benefit alignment**: Trial decoding and validation are **cheaper** for small content. Being more conservative (lower confidence → more validation) when it matters least (small files) is a win-win.

4. **Smooth, predictable behavior**: Linear scaling avoids arbitrary threshold discontinuities. A step function would create sudden behavior changes at threshold boundaries, while linear scaling provides gradual, intuitive confidence progression.

5. **Philosophical consistency**: "Honest about limitations" means acknowledging that charset/MIME detection is fundamentally harder with less data. Our confidence scores should reflect this reality.

## Size Scaling Formula

```python
def confidence_from_bytes_quantity(
    content: Content, behaviors: Behaviors = BEHAVIORS_DEFAULT
) -> float:
    return min(1.0, len(content) / behaviors.bytes_quantity_confidence_divisor)
```

**Default divisor**: 1024 bytes

This means:
- 512 bytes → 0.5 scaling factor
- 1024 bytes → 1.0 scaling factor (full confidence)
- 2048 bytes → 1.0 (capped at maximum)

## Detector-Specific Strategies

### Detectors With Intrinsic Confidence

These detectors provide their own confidence scores based on detection quality. We multiply by the size scaling factor.

#### chardet (Charset Detection)

```python
def _detect_via_chardet(
    content: Content, behaviors: Behaviors
) -> CharsetResult | types.NotImplementedType:
    try: import chardet
    except ImportError: return NotImplemented
    result_ = chardet.detect(content)
    charset, confidence = result_['encoding'], result_['confidence']

    # Scale confidence by content size
    size_factor = confidence_from_bytes_quantity(content, behaviors=behaviors)
    confidence = confidence * size_factor

    return CharsetResult(charset=charset, confidence=confidence)
```

**Rationale**: `chardet` reports confidence based on statistical analysis, but doesn't account for sample size adequacy. A 95% confidence on 10 bytes should be treated much more skeptically than 95% on 1000 bytes.

#### puremagic (MIME Type Detection)

```python
def _detect_via_puremagic(
    content: Content, behaviors: Behaviors
) -> MimetypeResult | types.NotImplementedType:
    try: import puremagic
    except ImportError: return NotImplemented
    try:
        matches = puremagic.magic_string(content)
        if not matches: return NotImplemented
        match = matches[0]  # Best match

        # Use puremagic's intrinsic confidence, scaled by size
        size_factor = confidence_from_bytes_quantity(content, behaviors=behaviors)
        confidence = match.confidence * size_factor

        return MimetypeResult(mimetype=match.mime_type, confidence=confidence)
    except (puremagic.PureError, ValueError):
        return NotImplemented
```

**Rationale**: `puremagic` provides confidence scores (typically 0.4-0.8) based on signature match quality. Longer, more specific signatures get higher confidence. Similar to `chardet`, these scores benefit from size scaling.

**Note**: The current implementation uses `puremagic.from_string(content, mime=True)` which returns a simple string. To access confidence, we need to use `puremagic.magic_string(content)` instead, which returns `PureMagicWithConfidence` objects.

### Detectors Without Intrinsic Confidence

These detectors only return a detection result without quality assessment. We assign a base confidence constant, then scale by size.

#### magic/libmagic (MIME Type Detection)

```python
def _detect_via_magic(
    content: Content, behaviors: Behaviors
) -> MimetypeResult | types.NotImplementedType:
    try: import magic
    except ImportError: return NotImplemented
    try: mimetype = magic.from_buffer(content, mime=True)
    except Exception: return NotImplemented

    # Use different base confidence for textual vs binary formats
    if is_textual_mimetype(mimetype):
        BASE_CONFIDENCE = 0.75  # Lower for text (heuristic-based)
    else:
        BASE_CONFIDENCE = 0.95  # Higher for binary (magic bytes)

    confidence = BASE_CONFIDENCE * confidence_from_bytes_quantity(
        content, behaviors=behaviors)
    return MimetypeResult(mimetype=mimetype, confidence=confidence)
```

**Rationale**:
- **Binary formats (0.95)**: libmagic excels at detecting structured binary formats with magic bytes (PNG: `\x89PNG`, PDF: `%PDF`, etc.). These are unambiguous byte patterns with decades of curated signatures.
- **Textual formats (0.75)**: Text detection is often heuristic-based. `text/plain` is frequently a fallback/guess. `text/html`, `text/xml`, and even `application/json` (which may be detected as `text/plain` on some platforms) are more ambiguous and context-dependent.

**Platform note**: `magic` behavior varies across platforms and versions. On Windows, JSON content may return `text/plain` instead of `application/json`. The textual/non-textual distinction handles this gracefully.

#### charset-normalizer (Charset Detection)

```python
def _detect_via_charset_normalizer(
    content: Content, behaviors: Behaviors
) -> CharsetResult | types.NotImplementedType:
    try: import charset_normalizer
    except ImportError: return NotImplemented
    result_ = charset_normalizer.from_bytes(content).best()
    charset = None if result_ is None else result_.encoding

    # charset-normalizer doesn't provide usable confidence
    # Use base constant scaled by size
    BASE_CONFIDENCE = 0.85
    confidence = BASE_CONFIDENCE * confidence_from_bytes_quantity(
        content, behaviors=behaviors)

    return CharsetResult(charset=charset, confidence=confidence)
```

**Rationale**:
- charset-normalizer has `coherence` and related attributes, but these are not reliable confidence metrics (often 0.0)
- Evaluation results showed: 92% accurate on UTF-8, but only 17% on Latin-1/CP1252
- Base confidence of 0.85 reflects that it's good but not as reliable as `chardet` (which provides its own confidence)
- Still higher than textual MIME detection (0.75) since charset detection is more targeted

## Confidence Constants Summary

| Detector | Type | Strategy | Base Confidence | Notes |
|----------|------|----------|-----------------|-------|
| `chardet` | Charset | Intrinsic × size | N/A (uses reported) | Statistical analysis |
| `puremagic` | MIME | Intrinsic × size | N/A (uses reported) | Signature match quality (0.4-0.8) |
| `magic` (binary) | MIME | Constant × size | 0.95 | Magic bytes, very reliable |
| `magic` (textual) | MIME | Constant × size | 0.75 | Heuristic-based, less reliable |
| `charset-normalizer` | Charset | Constant × size | 0.85 | Good for UTF-8, weaker for legacy |

## Example Confidence Calculations

### Small File (100 bytes)
Size factor: `100 / 1024 = 0.0977` (~0.1)

- **chardet** (0.95 raw): `0.95 × 0.1 = 0.095`
- **magic** binary (0.95 base): `0.95 × 0.1 = 0.095`
- **magic** textual (0.75 base): `0.75 × 0.1 = 0.075`
- **charset-normalizer** (0.85 base): `0.85 × 0.1 = 0.085`
- **puremagic** (0.8 raw): `0.8 × 0.1 = 0.08`

All appropriately conservative. With `trial_decode_confidence = 0.80`, all trigger validation.

### Medium File (512 bytes)
Size factor: `512 / 1024 = 0.5`

- **chardet** (0.95 raw): `0.95 × 0.5 = 0.475`
- **magic** binary (0.95 base): `0.95 × 0.5 = 0.475`
- **magic** textual (0.75 base): `0.75 × 0.5 = 0.375`
- **charset-normalizer** (0.85 base): `0.85 × 0.5 = 0.425`
- **puremagic** (0.8 raw): `0.8 × 0.5 = 0.4`

Still below 0.80 threshold, but closer. More validation occurs.

### Full Confidence (1024+ bytes)
Size factor: `1024 / 1024 = 1.0` (or higher, capped at 1.0)

- **chardet** (0.95 raw): `0.95 × 1.0 = 0.95`
- **magic** binary (0.95 base): `0.95 × 1.0 = 0.95`
- **magic** textual (0.75 base): `0.75 × 1.0 = 0.75`
- **charset-normalizer** (0.85 base): `0.85 × 1.0 = 0.85`
- **puremagic** (0.8 raw): `0.8 × 1.0 = 0.8`

Nice spread. Binary detections and high-confidence chardet skip validation. Textual MIME and charset-normalizer still trigger validation unless detection is very confident or sample is larger.

## Interaction with Behavior Thresholds

### `trial_decode_confidence` (default: 0.80)

Minimum confidence to skip trial decoding during charset detection.

With size scaling:
- Small files almost always trigger trial decode (good: cheap to validate)
- Medium files trigger if detector isn't confident
- Large files only skip if detector is confident

### `text_validate_confidence` (default: 0.80)

Minimum confidence to skip text validation.

Similar behavior: more validation on small samples, less on large confident detections.

## Special Cases

### Empty Content

Empty content (`b''`) always returns:
- Charset: default charset with 1.0 confidence
- MIME: `text/plain` with 1.0 confidence

No detection is needed, so confidence is absolute.

### Content with BOM

BOMs (Byte Order Marks) provide near-certainty for UTF-8/UTF-16 detection regardless of size. However:
- This is already handled in `_normalize_charset_detection()` which checks for BOM and adjusts charset accordingly
- No special confidence handling needed; chardet will report high confidence, which is appropriate

### Pure ASCII

Small pure ASCII samples (like `b"Hello"`) get scaled down confidence, but:
- ASCII is promoted to UTF-8 via `charset_promotions`
- Small ASCII content is cheap to validate
- Erring on the side of validation is fine

## Implementation Notes

### Current State (Before Changes)

- ✅ `chardet`: Returns raw confidence (no scaling)
- ✅ `charset-normalizer`: Uses `confidence_from_bytes_quantity()`
- ✅ `magic`: Uses `confidence_from_bytes_quantity()`
- ✅ `puremagic`: Uses `confidence_from_bytes_quantity()`

### Needed Changes

1. **Scale chardet confidence**: Multiply by size factor
2. **Add base constants**: Define base confidence for `magic` and `charset-normalizer`
3. **Textual/binary distinction for magic**: Use `is_textual_mimetype()` to select base confidence
4. **Extract puremagic confidence**: Switch from `from_string()` to `magic_string()` to access confidence scores

## Documentation for Users

Users should understand that confidence scores in detextive are composite:

> **Confidence scores reflect both detection quality and sample adequacy.**
>
> A confidence of 0.95 from detextive means both:
> - The detector is highly confident in its result
> - There is sufficient content for reliable detection
>
> For small samples (< 1024 bytes), confidence is proportionally reduced to encourage validation. This is intentional: charset and MIME type detection are fundamentally less reliable with less data.

## Rationale: Why Not Step Functions?

An alternative approach would be minimum size thresholds:

```python
if len(content) < 1024:
    confidence = min(confidence, 0.79)  # Force below threshold
```

**Problems with this approach**:
1. **Discontinuous behavior**: 1023 bytes → untrusted, 1024 bytes → fully trusted
2. **Arbitrary boundary**: Why 1024? Why not 512 or 2048?
3. **Loss of information**: A 1000-byte detection is more reliable than a 100-byte detection, but both get capped

Linear scaling is more principled, predictable, and preserves relative quality differences across sample sizes.

## Future Considerations

### Tunable Parameters

If users want different size/confidence tradeoffs, they can adjust:

```python
behaviors = Behaviors(
    bytes_quantity_confidence_divisor=512,  # Smaller threshold
    trial_decode_confidence=0.70,           # Lower bar for skipping validation
)
```

### Alternative Scaling Functions

Linear scaling is simple and effective, but alternatives could be considered:

```python
# Logarithmic (slower growth, more conservative)
confidence = math.log(len(content) + 1) / math.log(1025)

# Sigmoid (smooth S-curve with inflection point)
confidence = 1 / (1 + math.exp(-k * (len(content) - midpoint)))
```

For now, linear scaling aligns with the design philosophy: simple, honest, and predictable.

## Related Documents

- `.auxiliary/notes/decode-refactor.md` - Context-based trial order and design philosophy
- `.auxiliary/notes/charset-detector-evaluation-results.md` - Empirical detector performance data
- `documentation/architecture/designs/001-python-api.rst` - API design including confidence scoring
