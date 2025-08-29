### Interface Structure and Call Hierarchy

Based on the provided release 2.0 interface architecture document, the current
source code (e.g., `detection.py` and `__init__.py`), and the suggestions from
GPT-5 and Opus 4.1, I'll outline a refined structure for the `detextive`
package's interface. The goal is to maintain functional simplicity while
addressing pain points like redundant detection, context loss, and rigid
validation. The architecture doc's layered approach (Primitive Detectors →
Validation Functions → Public API) is a strong foundation, but we can enhance
it for better modularity, especially around text validation (e.g., integrating
`is_valid_text` as a key validator).

#### Key Principles Guiding the Design
- **Modularity and Reusability**: Primitives should be low-level and
  independent, validators composable, and public APIs opinionated wrappers that
  orchestrate them based on context (e.g., content bytes, location, HTTP
  headers).
- **Context-Aware Execution**: Prioritize available hints (e.g., Content-Type
  header) before falling back to expensive analysis (e.g., magic bytes or full
  content scans).
- **Configurability Without Complexity**: Use DTOs (dataclasses) for behaviors
  and profiles to allow customization while providing sensible defaults and
  predefined options.
- **Error Handling Flexibility**: Support the error class provider pattern from
  the doc to eliminate boilerplate in downstream integrations.
- **Performance**: Single-pass where possible (e.g., in validation),
  conditional execution (skip validators if not needed), and early exits.
- **Backwards Compatibility**: Enhance existing functions (e.g.,
  `detect_mimetype_and_charset`) with new optional parameters without breaking
  signatures.
- **Integration with Validation**: `is_valid_text` fits as a Layer 2 validator,
  called conditionally during MIME/charset detection (e.g., in trial decodes)
  or standalone for decoded text.

#### Proposed Call Hierarchy
The hierarchy follows the architecture doc's layers but expands Layer 2 to
include text validation explicitly. Public APIs (Layer 3) orchestrate calls to
Layers 1-2 based on a `Behaviors` DTO (from the doc) and a new
`TextValidationProfile` DTO (for `is_valid_text`). Arrows indicate call flow;
dashed lines show optional/configurable paths.

```
┌─────────────────────────────────────────────────────────────┐
│                    Layer 3: Public API                      │
│  - detect_charset(content, [content_type, behaviors])       │
│  - detect_mimetype_charset(content, [location, content_type, behaviors, error_class_provider]) │
│  - detect_mimetype_charset_linesep(content, [location, content_type, behaviors, error_class_provider]) │
│  - is_textual_mimetype(mimetype)  [unchanged, simple utility] │
│  - is_textual_content(content)     [enhanced to use behaviors] │
│                                                             │
│  (Orchestrate based on context; apply Behaviors; handle errors via provider) │
└──────────────────────────────────────────┬──────────────────┘
                                           │
                                           ▼
┌──────────────────────────────────────────┼──────────────────┐
│                  Layer 2: Validators     │                  │
│  - _validate_charset_with_trial_decode(content, charset, [profile]) │
│  - _validate_printable_content(text, profile)  [core of is_valid_text] │
│  - _validate_no_ansi_escapes(text)     [optional, for TERMINAL_SAFE_NOANSI] │
│  - is_valid_text(text, profile)        [public-facing wrapper for above] │
│                                          │                  │
│  (Composable; use TextValidationProfile; single-pass with early exits) │
└──────────────────────────────────────────┼──────────────────┘
                                           │
                                           ▼
┌──────────────────────────────────────────┼──────────────────┐
│              Layer 1: Primitives         │                  │
│  - _detect_mimetype_from_header(content_type)               │
│  - _detect_mimetype_from_extension(location)                │
│  - _detect_mimetype_from_magic(content)                     │
│  - _detect_charset_from_header(content_type)                │
│  - _detect_charset_from_content(content)                    │
│  - _detect_linesep_from_content(content)                    │
│                                                             │
│  (Low-level, independent detectors; no validation here)     │
└─────────────────────────────────────────────────────────────┘
```

- **Layer 1 (Primitives)**: Pure detection without validation or orchestration.
  These are internal but could be exposed if needed. They return
  `Absential[str]` (e.g., absent if undetectable) to avoid exceptions at this
  level.
  - Called conditionally: E.g., if `content_type` is provided, prefer
    header-based detectors over magic/content analysis.
  - Enhancements: Add optional libmagic support (via `python-magic` as an extra
    dependency) as a fallback to `puremagic` for better coverage.

- **Layer 2 (Validators)**: Focus on post-detection checks. `is_valid_text`
  lives here as a public wrapper around `_validate_printable_content`, which
  implements the heuristic logic. Validators raise specific exceptions (e.g.,
  `TextualMimetypeInvalidity`) unless suppressed via `Behaviors`.
  - Integration: During a trial decode in Layer 3 (e.g.,
    `detect_mimetype_charset`), call `_validate_charset_with_trial_decode`
    which decodes and then calls `is_valid_text` if
    `behaviors.validate_printable == 'always'` or `'as-needed'`.
  - Configurability: Driven by `TextValidationProfile` (see DTOs below).

- **Layer 3 (Public API)**: High-level functions that fuse context, apply
  behaviors, and orchestrate lower layers. These are the main entry points.
  - Example Flow in `detect_mimetype_charset`:
    1. If `content_type` present: Call Layer 1 header primitives for
       mimetype/charset.
    2. Fallback to location/extension if absent.
    3. Final fallback to content/magic.
    4. If textual mimetype detected and `behaviors.trial_decode ==
       'as-needed'`: Call Layer 2 trial decode + validation.
    5. Handle errors via `error_class_provider` (e.g., map to downstream
       exceptions or return absent).
  - Enhancements to Existing Functions: Add optional `content_type`,
    `behaviors`, and `error_class_provider` kwargs to functions like
    `detect_mimetype_and_charset` without changing required args.

This hierarchy reduces redundancy (e.g., no repeated content scans) and allows
conditional skipping (e.g., no validation for non-textual content unless
forced).

### Structuring `is_valid_text`
The current `_is_probable_textual_content` is a good starting heuristic but has
issues noted in our discussion and the LLM responses: redundant passes,
ASCII-only control checks, incomplete Unicode handling (e.g., misses U+2028
'Zl' category, which is non-printable and often renders as garbage in
terminals), and lack of configurability. GPT-5 and Opus 4.1 both recommend a
single-pass, Unicode-aware approach with early exits, hard bans (e.g., on ESC
for terminal safety), and configurable thresholds.

We'll replace/augment `_is_probable_textual_content` with `is_valid_text` as a
more robust validator. It will:
- Use a single pass over the string.
- Leverage `unicodedata.category` for consistent Unicode classification (better
  than `isprintable()` alone, as it catches all 'C*' categories: Cc controls,
  Cf formats like bidi, Cs surrogates, etc.).
- Support profiles (as per your TODO: TEXTUAL, TERMINAL_SAFE, etc.) via a DTO.
- Hard-ban disruptive chars (e.g., ESC `\x1b` to prevent ANSI sequences) by
  default for safety.
- Allow common whitespace (`\t\n\r`) but configurable.
- Early-exit if thresholds exceeded.
- Optionally scan for full ANSI sequences (e.g., via regex) if
  `allow_ansi=False`.
- Thresholds configurable (e.g., max 5% controls for strict profiles).

This addresses terminal/printer safety: No garbage from controls, no bidi
spoofing (ban 'Cf' by default), no escape sequences. For U+2028 specifically:
It's 'Zl', fails `isprintable()`, and counts as a control unless explicitly
allowed—leading to failure in strict profiles, which is desirable as it doesn't
reliably break lines in terminals.

#### Proposed Implementation for `is_valid_text`
Add this to `detection.py` (replacing `_is_probable_textual_content` usage in
`_validate_mimetype_with_trial_decode`).

```python
import re
import unicodedata

from . import __
from .exceptions import TextualMimetypeInvalidity

# Precompiled for efficiency; matches common ANSI CSI/OSC sequences
_ANSI_ESCAPE_RE = re.compile(r'\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~]|\][^\x07]*\x07)')

class TextValidationProfile(__.immut.DataclassObject):
    ''' Configuration for text validation heuristics. '''
    name: __.typx.Annotated[
        str, __.ddoc.Doc("Profile name for identification.")
    ] = 'TEXTUAL'
    min_printable_ratio: __.typx.Annotated[
        float, __.ddoc.Doc("Minimum fraction of printable characters (0.0-1.0).")
    ] = 0.8
    max_control_ratio: __.typx.Annotated[
        float, __.ddoc.Doc("Maximum fraction of disallowed control/format characters.")
    ] = 0.1
    allowed_whitespace: __.typx.Annotated[
        frozenset[str], __.ddoc.Doc("Explicitly allowed whitespace/control chars.")
    ] = frozenset({'\t', '\n', '\r'})
    banned_chars: __.typx.Annotated[
        frozenset[str], __.ddoc.Doc("Characters that cause immediate failure.")
    ] = frozenset({'\x1b'})  # ESC by default
    ban_categories: __.typx.Annotated[
        frozenset[str], __.ddoc.Doc("Unicode categories to treat as controls (e.g., 'Cf' for bidi).")
    ] = frozenset({'Cc', 'Cf', 'Cs', 'Co', 'Cn', 'Zl', 'Zp'})
    allow_ansi_escapes: __.typx.Annotated[
        bool, __.ddoc.Doc("If False, scan and reject ANSI escape sequences.")
    ] = False

# Predefined profiles
PROFILE_TEXTUAL = TextValidationProfile(
    name='TEXTUAL', min_printable_ratio=0.8, max_control_ratio=0.1,
    ban_categories=frozenset({'Cc', 'Cf'})  # Exclude C0/C1 minus whitespace, bidi
)
PROFILE_TERMINAL_SAFE = TextValidationProfile(
    name='TERMINAL_SAFE', min_printable_ratio=0.95, max_control_ratio=0.05,
    allow_ansi_escapes=True  # Allows escapes but bans incomplete/disruptive ones
)
PROFILE_TERMINAL_SAFE_NOANSI = TextValidationProfile(
    name='TERMINAL_SAFE_NOANSI', min_printable_ratio=0.95, max_control_ratio=0.0,
    allow_ansi_escapes=False
)
PROFILE_PRINTER_SAFE = TextValidationProfile(
    name='PRINTER_SAFE', min_printable_ratio=0.98, max_control_ratio=0.0,
    banned_chars=frozenset({'\x1b', '\x0c'})  # ESC and Form Feed
)

def is_valid_text(
    text: str,
    profile: __.Absential[TextValidationProfile] = __.absent
) -> bool:
    ''' Validates decoded text against a profile.

        Raises TextualMimetypeInvalidity if invalid (for use in trial decodes).
        Returns True if valid according to profile heuristics.
    '''
    if __.is_absent(profile): profile = PROFILE_TEXTUAL
    if not text: return False

    n = len(text)
    printable = 0
    controls = 0

    # Early check for ANSI if disallowed
    if not profile.allow_ansi_escapes and _ANSI_ESCAPE_RE.search(text):
        raise TextualMimetypeInvalidity('unknown', 'text/plain')  # Or custom msg

    # Precompute for speed
    category_func = unicodedata.category
    allowed_ws = profile.allowed_whitespace
    banned = profile.banned_chars
    ban_cats = profile.ban_categories

    min_print_needed = int(profile.min_printable_ratio * n)
    max_controls_allowed = int(profile.max_control_ratio * n)

    for i, c in enumerate(text):
        if c in banned:
            raise TextualMimetypeInvalidity('unknown', 'text/plain')

        if c in allowed_ws:
            printable += 1
            continue

        cat = category_func(c)
        if cat in ban_cats or cat.startswith('C'):  # Catch all C* if not specified
            controls += 1
            if controls > max_controls_allowed:
                raise TextualMimetypeInvalidity('unknown', 'text/plain')
        elif c.isprintable():
            printable += 1

        # Early exit if impossible to meet threshold
        remaining = n - (i + 1)
        if printable + remaining < min_print_needed:
            raise TextualMimetypeInvalidity('unknown', 'text/plain')

    if printable < min_print_needed:
        raise TextualMimetypeInvalidity('unknown', 'text/plain')
    return True
```

- **Why This Structure?** Combines best ideas: Single pass (efficiency),
  Unicode categories (comprehensive), configurable via DTO (flexible), hard
  bans/ANSI check (safety). Profiles allow easy switching (e.g., TEXTUAL is
  lenient on line separators like U+2028; TERMINAL_SAFE bans them).
- **Integration**: In `_validate_mimetype_with_trial_decode`, decode then call
  `is_valid_text(text, profile=behaviors.text_profile)` (extend `Behaviors` DTO
  with a `text_profile` field).
- **Custom Profiles**: Users can create their own, e.g.,
  `TextValidationProfile(min_printable_ratio=0.9, ban_categories={'Cf'})` for
  bidi-sensitive apps.

### Function Signatures and DTOs

#### Enhanced Existing Signatures
Keep core args unchanged; add optionals for v2.0 features.

```python
def detect_mimetype_and_charset(
    content: Content,
    location: Location, *,
    mimetype: __.Absential[str] = __.absent,
    charset: __.Absential[str] = __.absent,
    content_type: __.Absential[str] = __.absent,  # New: HTTP header
    behaviors: __.Absential[Behaviors] = __.absent,  # From arch doc
    error_class_provider: __.Absential[ErrorClassProvider] = __.absent
) -> tuple[str, __.typx.Optional[str]]:
    ''' ... [doc from current code, plus enhancements] '''
```

Similar for other publics like `detect_charset` (as in arch doc).

#### New/Updated DTOs
- **Behaviors** (from arch doc, slightly expanded):
  ```python
  class Behaviors(__.immut.DataclassObject):
      trial_decode: TriState = 'as-needed'
      validate_printable: TriState = 'as-needed'
      text_profile: __.Absential[TextValidationProfile] = __.absent  # New: Link to validation
      printable_threshold: float = 0.8  # Override if no profile
      assume_utf8_superset: bool = True
  ```
- **TextValidationProfile**: As above; serves as DTO for validation config.
- **ErrorClassProvider**: As in arch doc (callable mapping names to exceptions).

This setup allows seamless integration: Public APIs use `Behaviors` to control
orchestration/validation, while `is_valid_text` uses its profile DTO for
fine-grained text checks. If needed, add a `DetectionResult` DTO for returning
structured data (e.g., dataclass with mimetype, charset, linesep, validity:
bool).
