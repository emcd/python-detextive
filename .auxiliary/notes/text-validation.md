# Text Validation Algorithm Design

## Summary

This document captures the design decisions for implementing text validation in
Detextive v2.0, based on analysis of the `TextValidationProfile` interface and
real-world validation requirements.

## Core Problem

**Primary Use Case**: Textuality detection - "Is this decoded content actually
text, or binary data that happened to decode without errors?"

This is distinct from terminal safety, which has different requirements and
tolerance levels.

## Key Design Insights

### 1. Character Classification Precedence

Unicode categories don't align with practical "acceptability" for text
validation. The solution is an **acceptance-first** classification system:

```python
def classify_character(char: str, profile: TextValidationProfile) -> str:
    # 1. Explicit acceptance wins (overrides everything)
    if char in profile.acceptable_characters:
        return 'acceptable'

    # 2. Explicit rejection wins (performance optimization)
    if char in profile.rejectable_characters:
        return 'rejectable'

    # 3. Category-based rejection
    if unicodedata.category(char) in profile.rejectable_families:
        return 'rejectable'

    # 4. Extended printability as fallback
    if is_text_printable(char):
        return 'acceptable'
    else:
        return 'questionable'
```

### 2. Counting Methodology

**Exclude acceptable characters from all ratio calculations**. This makes thresholds intuitive:

- Only "questionable" characters are evaluated against ratios
- `printables_ratio_min=0.95` means "95% of uncertain characters must be printable"
- `rejectables_ratio_max=0.0` means "0% of uncertain characters can be problematic"

Examples:
- `"Hello\tWorld\n"` → Only `"Hello World"` counted → 100% printable ✓
- `"Hello\x00World"` → `"Hello World\x00"` counted → ~91% printable, ~9% rejectable ✗

## Recommended Implementation

### TextValidationProfile Structure

```python
@dataclasses.dataclass
class TextValidationProfile:
    # Core controls
    reject_c0_controls: bool = True
    acceptable_characters: frozenset = frozenset({'\t', '\n'})
    rejectable_characters: frozenset = frozenset()
    rejectable_families: frozenset = frozenset({'Cc', 'Cf'})

    # Ratio thresholds
    printables_ratio_min: float = 0.85
    rejectables_ratio_max: float = 0.0

    # Performance
    sample_quantity: int = 8192

    def __post_init__(self):
        if self.reject_c0_controls:
            c0_controls = {chr(i) for i in range(32)} - self.acceptable_characters
            self.rejectable_characters = self.rejectable_characters | c0_controls
```

### Extended Printability Function

```python
def is_text_printable(char: str) -> bool:
    """Printable for text purposes (not just terminal display)."""
    if char.isprintable():
        return True

    # Combining marks are textual even if not "printable"
    category = unicodedata.category(char)
    if category.startswith('M'):  # Mn, Mc, Me - all marks
        return True

    return False
```

### Validation Algorithm

```python
def is_valid_text(text: str, profile: TextValidationProfile) -> bool:
    if not text:
        return False

    # Sample for performance
    sample_size = min(len(text), profile.sample_quantity)
    sample = text[:sample_size]

    questionable_count = 0
    printable_count = 0
    rejectable_count = 0

    # Pre-compute for performance
    acceptable = profile.acceptable_characters
    rejectable_chars = profile.rejectable_characters
    rejectable_families = profile.rejectable_families

    for char in sample:
        if char not in acceptable:
            questionable_count += 1

            # Fast path: explicit rejectable (set lookup)
            if char in rejectable_chars:
                rejectable_count += 1
            # Slow path: category lookup
            elif unicodedata.category(char) in rejectable_families:
                rejectable_count += 1
            elif is_text_printable(char):
                printable_count += 1

            # Early exit on too many rejectables
            if rejectable_count > questionable_count * profile.rejectables_ratio_max:
                return False

    if questionable_count == 0:
        return True

    return printable_count >= questionable_count * profile.printables_ratio_min
```

## Recommended Profile: Textuality Detection

```python
PROFILE_TEXTUAL = TextValidationProfile(
    reject_c0_controls=True,
    acceptable_characters=frozenset({'\t', '\n'}),  # Conservative whitespace
    rejectable_families=frozenset({'Cc', 'Cf'}),   # Controls + formats only
    printables_ratio_min=0.85,  # Accommodate combining chars, tabular content
    rejectables_ratio_max=0.0,  # Zero tolerance for control characters
    sample_quantity=8192,
)
```

## Edge Cases Handled

### 1. Tabular Content with Many Tabs
- Tabs excluded from ratio calculations
- Remaining content validated normally
- Example: `"Name\tAge\tCity"` → Only `"NameAgeCity"` evaluated

### 2. International Text with Combining Characters
- Combining marks (category `M*`) treated as textual
- Lower printable threshold (85%) accommodates mark-heavy text
- Examples: phonetic transcription, Vietnamese tones, Arabic diacritics

### 3. C0 Control Character Performance
- Pre-computed set of C0 controls for fast lookup
- Slight performance advantage over range checks
- Cleaner algorithm with uniform set-based logic

## Key Benefits

1. **Precise Control**: Explicit acceptance/rejection lists override categories
2. **Performance Optimized**: Single pass with early exits, pre-computed sets
3. **Unicode Aware**: Proper handling of combining marks and international text
4. **Intuitive Configuration**: Ratios apply only to uncertain characters
5. **Binary Detection**: Zero tolerance for control characters catches binary masquerading as text

## Implementation Priority

This text validation system addresses the primary blocking issue identified in `design-reconciliation.md` - the missing `is_valid_text` implementation. It provides a sophisticated, configurable foundation for distinguishing legitimate textual content from binary data that happens to decode successfully.
