# Charset Detection Design

## Trial Codecs Usage Patterns

### Context

The `trial_codecs` behavior parameter controls which character sets are tried
during decoding operations. Analysis revealed three distinct usage patterns
with different requirements, leading to platform-specific failures when the
same codec order was used for all contexts.

### Usage Patterns

#### Opportunistic Decoding

**Goal**: Find any charset that produces readable text from content.

**Context**: The `decode()` function and general content decoding.

**Strategy**: Try multiple codecs including OS default until one succeeds.

**Codecs**: `(OsDefault, UserSupplement, FromInference)`

**Rationale**: On modern systems (Linux/Mac), OsDefault is UTF-8, providing a
good first guess that corrects common chardet misdetections.

#### Authoritative Validation

**Goal**: Verify that a specific authoritative charset works (no fallbacks).

**Context**: HTTP `Content-Type` headers, MIME type charset validation.

**Strategy**: Only try the explicitly specified charset.

**Codecs**: `(FromInference,)`

**Rationale**: When a charset is authoritatively specified (e.g., HTTP header),
we must test that exact charset, not find alternatives. OS default fallbacks
would mask validation failures.

#### Detection Confirmation

**Goal**: Validate detected charset with optional user hint as fallback.

**Context**: Charset detection confirmation in `_confirm_charset_detection()`.

**Strategy**: Try detected charset, then user supplement if detection fails.

**Codecs**: `(UserSupplement, FromInference)`

**Rationale**: Validates the detection result but respects user knowledge as
a fallback. Excludes OS default to prevent Windows cp1252 from masking
detection failures.

### Implementation

Each context overrides `trial_codecs` via `__.dcls.replace()` before
calling codec trial functions:

```python
# Authoritative validation
behaviors_strict = __.dcls.replace(
    behaviors,
    trial_codecs = ( _CodecSpecifiers.FromInference, ) )

# Detection confirmation
behaviors_no_os = __.dcls.replace(
    behaviors,
    trial_codecs = (
        _CodecSpecifiers.UserSupplement,
        _CodecSpecifiers.FromInference,
    ) )
```

### Platform Considerations

**Windows Issue**: OS default charset is cp1252, an 8-bit encoding that
decodes any byte sequence. When used in validation contexts, it masks
detection failures by succeeding when it shouldn't.

**Solution**: Exclude `OsDefault` from validation and confirmation contexts,
using it only for opportunistic decoding where fallbacks are desired.
