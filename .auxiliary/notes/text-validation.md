# Text Validation and the Irrelevance of Confidence Thresholds

## Summary

The `text_validate_confidence` parameter should be removed. Text validation checks whether decoded content looks like real text (not binary data that happened to decode successfully). This is orthogonal to charset detection confidence and doesn't benefit from a confidence threshold.

## Current Behavior

### `text_validate_confidence` Usage

Currently used in `_validate_text()` to decide whether to validate:

```python
match behaviors.text_validate:
    case BehaviorTristate.AsNeeded:
        should_validate = confidence < behaviors.text_validate_confidence
```

Default threshold: 0.80

### Where Validation Is Called

1. **From `_attempt_decode_http_content_type()`**:
   - Passes `result.confidence` from `attempt_decodes()`
   - This is size-based confidence: `confidence_from_bytes_quantity()`

2. **From `_attempt_decodes()` (main decode path)**:
   - Passes `0.0` confidence (hardcoded!)
   - **Always validates** regardless of threshold

## What Validation Actually Checks

`PROFILE_TEXTUAL` (the default validation profile) checks:

- **Control characters**: Only allows `\t`, `\n`, `\r`, plus bidi/zero-width/formatting characters
- **Rejectable categories**: Rejects Unicode categories:
  - `Cc` (control characters)
  - `Cf` (format characters)
  - `Co` (private use)
  - `Cs` (surrogate)
- **Printables ratio**: Requires ≥85% printable characters
- **Explicit rejects**: DELETE character (0x7F)

### What Validation Catches

Validation catches **binary/non-textual data that successfully decoded**:

- Binary PNG data decoded as CP1252 → fails printables ratio
- UTF-16 data decoded as UTF-8 → produces garbage with control characters
- Random binary content decoded as ISO-8859-1 → fails printables ratio
- Mojibake from wrong charset → may contain unprintables

**Key insight**: Any charset can decode binary data without raising `UnicodeDecodeError`. Validation is the only way to catch these false positives.

## Why Confidence Threshold Doesn't Help

### 1. Always 0.0 in Main Decode Path

In `_attempt_decodes()`, confidence is hardcoded to `0.0`:

```python
return _validate_text(
    text, 0.0,  # ← Always 0.0
    behaviors=behaviors, profile=profile, location=location)
```

This means:
- Validation **always runs** in the main decode path
- The `text_validate_confidence` threshold is never actually checked
- The parameter is effectively dead code for normal decoding

### 2. Validation Is Not About Detection Quality

Confidence reflects: "How sure are we this is the right charset?"

Validation checks: "Does this look like real text?"

These are **orthogonal concerns**:
- High-confidence UTF-8 detection can still produce mojibake if the actual charset was CP1252
- Low-confidence detection on small sample might be correct and produce valid text
- Wrong charset with high confidence → valid-looking text that happens to be garbage

### 3. Sample Size Doesn't Reduce Need for Validation

The argument for confidence threshold might be:
> "Large files with high-confidence detection don't need validation"

But this is wrong because:
- Large binary files (images, executables) can still decode as text
- HTTP headers can lie about charset
- Validation is cheap (character category checks)
- Better to validate anyway

### 4. Any Charset Can Encode Binary Data

All charsets can represent control characters:
- UTF-8: `\x00`, `\x01`, `\x02`, etc.
- CP1252: Control chars in 0x00-0x1F range
- ISO-8859-1: Decodes a very broad range of byte values

There's no charset-based reason to skip validation.

## Proposed Changes

### Remove Confidence Threshold

Change validation logic from:

```python
match behaviors.text_validate:
    case BehaviorTristate.AsNeeded:
        should_validate = confidence < behaviors.text_validate_confidence
```

To:

```python
match behaviors.text_validate:
    case BehaviorTristate.AsNeeded:
        should_validate = True  # Always validate when AsNeeded
```

Or simplify the tristate entirely:
- `Always`: Validate
- `Never`: Don't validate
- `AsNeeded`: **Remove** (was equivalent to Always in practice)

### Simplify to Boolean

Even simpler option:

```python
class Behaviors:
    text_validate: bool = True  # Just True/False
```

But keeping the tristate maintains API compatibility and clarity:
- `Always`: Validate (explicit)
- `AsNeeded`: Validate (matches current behavior)
- `Never`: Don't validate (opt-out for performance)

### Remove Parameter

Delete from `Behaviors`:

```python
text_validate_confidence: float = 0.80  # ← Remove this
```

### Update Signature

`_validate_text()` can keep the confidence parameter for now (for backward compatibility in internal calls), but ignore it:

```python
def _validate_text(
    text: str, confidence: float, /, *,  # confidence unused
    behaviors: BehaviorsArgument,
    profile: ProfileArgument,
    location: LocationArgument,
) -> str:
    # Don't check confidence, just validate based on tristate
    ...
```

Or remove it entirely and update all call sites.

## Why Validation Is Important

Validation is **critical** for detextive's reliability:

1. **Catches wrong charsets**: ISO-8859-1 can decode UTF-8 as mojibake
2. **Catches binary data**: Images, executables, etc. that decode without errors
3. **Provides meaningful errors**: Better to fail with "TextInvalidity" than return garbage
4. **Aligns with design philosophy**: "Honest about limitations" → validate results

## Performance Considerations

**Validation is cheap**:
- Samples only first 8192 characters by default (`profile.sample_quantity`)
- Character category lookup is O(1) with Unicode data
- Ratio calculations are simple arithmetic
- Negligible compared to charset detection

**No need to skip validation for performance.**

## Recommendation

1. **Remove `text_validate_confidence` parameter** from `Behaviors`
2. **Keep `text_validate` tristate** for user control
3. **Always validate when `AsNeeded`** (remove confidence check)
4. **Update documentation** to clarify that validation is about textuality, not confidence
5. **Update vulturefood.py** to remove `text_validate_confidence` entry

This simplifies the API, removes dead code, and aligns behavior with actual needs.

## Related Documents

- `.auxiliary/notes/confidence.md` - Confidence scoring strategy
- `.auxiliary/notes/decode-refactor.md` - Design philosophy and simplification
- `sources/detextive/validation.py` - Validation profiles and logic
