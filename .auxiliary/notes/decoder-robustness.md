# Decoder Robustness: Detection vs Validation

## Background

The `decode()` function must balance two concerns:
1. **Security**: Don't decode binary data as text (prevents garbage/mojibake)
2. **Robustness**: Don't reject valid text due to imperfect MIME detection

Commit cda5ad2 fixed a bug where binary data detected as UTF-16-LE was being decoded into garbage by making `decode()` reject all non-textual MIME types. This was correct but exposed a platform-specific issue: `libmagic` on MacOS CI misdetects plain ASCII text as `application/octet-stream`.

## Option 2: Improve MIME Type Detection (Implemented)

**Status**: Implemented in detectors.py

**Approach**: When MIME detection returns non-textual with low confidence, validate via charset-based detection before accepting the result.

**Logic**:
```python
# In detect_mimetype_confidence():
try_charset = (
        result is NotImplemented
    or  (
            not _mimetypes.is_textual_mimetype( result.mimetype )
        and result.confidence < behaviors.trial_decode_confidence ) )

if try_charset and not __.is_absent( charset ):
    result_from_charset = _detect_mimetype_from_charset(...)
    if result_from_charset.mimetype == 'text/plain':
        return result_from_charset
```

**What it solves**:
- Plain text misdetected as binary (low confidence) → validated via charset
- Maintains security: high-confidence binary detection is trusted
- Improves general robustness for uncertain detections

**Philosophy**: Detection layer should be smart about uncertainty. When a detector is unsure, use the more robust tool (charset + text validation) to validate.

## Option 3: Decode as Final Arbiter (Future Enhancement)

**Status**: Not implemented; reserved for future if needed

**Approach**: When MIME type says "binary" but charset detection has high confidence, attempt decoding anyway and let text validation be the final arbiter.

**Logic**:
```python
# In decode(), around line 76-78:
if not _mimetypes.is_textual_mimetype( mimetype_result.mimetype ):
    # MIME type says binary, but if charset detection had high confidence,
    # we might be dealing with plain text that lacks magic bytes.
    # Try decoding anyway and let text validation be the arbiter.
    if charset_result.confidence < behaviors.trial_decode_confidence:
        raise _exceptions.ContentDecodeImpossibility( location = location )
    # Otherwise: proceed to decode, text validation will reject if binary
```

**What it would solve**:
- **High-confidence** wrong MIME detection with correct charset detection
  - Example: Magic confidently says `application/octet-stream` (wrong)
  - Charset confidently says `utf-8` (correct)
  - Option 2: Trusts MIME (high confidence), doesn't validate via charset
  - Option 3: Would decode anyway, text validation catches if MIME was right

**Philosophy**: Trial decode + text validation is the most robust tool in our arsenal; everything else is a heuristic. When charset detection is confident, decode and validate even if MIME detection disagrees.

**Tradeoffs**:
- **Pro**: Maximum robustness against detection failures
- **Pro**: Aligns with philosophy that validation is ultimate truth
- **Pro**: Handles small files where confidence is typically low
- **Con**: Performance cost of decoding potentially binary data
- **Con**: More lenient than Option 2 (could allow more edge cases through)

**When to implement**:
- If we encounter cases where high-confidence MIME detection is consistently wrong
- If charset + text validation catches these cases reliably
- Currently seems like a rare edge case; Option 2 handles the known issues

## Decision Rationale

**Option 2 is sufficient** because:
1. The CI issue was specifically about **low-confidence** misdetection
2. High-confidence detections from `libmagic` are generally reliable
3. Charset-based validation already tries decode + text validation
4. Keeps architecture clean: detection handles detection, decode handles decoding

**Reserve Option 3** for future if we discover:
- Patterns of high-confidence wrong MIME detection
- Cases where charset + validation would catch what MIME missed
- Evidence that the performance cost is worthwhile
