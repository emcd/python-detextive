# Decode Refactor Progress

## Overview

This document tracks the progress of the `decode` function refactor, aiming to simplify the charset detection and decoding process by moving towards a context-aware trial order (User -> OS -> Python -> Detection) and reducing complexity around permissive/restrictive categorization.

## Comparisons: `decode-refactor` vs `master`

### `sources/detextive/decoders.py`
- **Refactored `decode` function**: Now implements the simplified logic.
- **New `_attempt_decodes`**: Implements the trial order:
    1.  Prepares charsets using `_prepare_charsets` (User, OS, Python, Detection).
    2.  Splits candidates into `restrictives` and `permissives`.
    3.  Tries `restrictives` first, then `permissives`.
- **New `_prepare_charsets`**: Collects charsets and sorts them into permissive/restrictive lists based on `is_permissive_charset`.
- **New `_validate_text`**: Centralized text validation logic.
- **BOM Handling**: Uses `behaviors.remove_bom` to normalize charsets (e.g., `utf-8` -> `utf-8-sig`).
- **TODO**: Deprecation warnings for `mimetype_*` arguments.

### `sources/detextive/charsets.py`
- **`is_permissive_charset`**: Added to identify charsets that accept all byte sequences (e.g., ISO-8859-*).
- **`attempt_decodes`**: Updated to use `set` for trials and `normalize_charset` with `bom_cognizant`.
- **`normalize_charset`**: Added `bom_cognizant` parameter.
- **`_charsets_permissive`**: Cache for permissive checks.
- **TODO**: Accretive dictionary comment.

### `sources/detextive/detectors.py`
- **`detect_charset_confidence`**: Defaults to `default` charset instead of hardcoded 'utf-8' when content is empty.

### `sources/detextive/inference.py`
- **`validate_httpct_charset`**: Added helper.

### `sources/detextive/core.py`
- **`Behaviors`**: Added `remove_bom` field (default `True`).

## Current Status

The simplified design described in `.auxiliary/notes/decode-refactor.md` has been largely implemented. The logic follows the "Context-based trial order".

## Issues & Remaining Work

1.  **Test Failures**:
    - `tests/test_000_detextive/test_220_charsets.py`: `test_220_codec_specifiers_user_supplement` fails.
        - Expects `utf-8`, gets `utf-8-sig`.
        - Caused by `behaviors.remove_bom=True` default and `normalize_charset` converting `utf-8` to `utf-8-sig`.
        - Action: Update test to expect `utf-8-sig` or allow configuring `remove_bom` in test.

2.  **Code Cleanup**:
    - Address `TODO` in `decoders.py`: Deprecation warnings for `mimetype_*`.
    - Address `TODO` in `charsets.py`: Accretive dictionary.

3.  **Verification**:
    - Ensure the new `decode` logic in `decoders.py` is properly tested. Current tests might be testing `charsets.attempt_decodes` which is used by `_attempt_decode_http_content_type` but the main `decode` path uses `decoders._attempt_decodes`.

4.  **Refactor Review**:
    - `decoders.py` has a local `_attempt_decodes` and `charsets.py` has `attempt_decodes`. This duplication/naming should be reviewed. `charsets.attempt_decodes` is still used for HTTP content type decoding.

## Next Steps

1.  Fix the failing test `test_220_charsets.py`.
2.  Implement deprecation warnings.
3.  Add tests specifically covering the new `decoders.decode` logic and trial order.
4.  Verify behavior with CP1252 vs UTF-8 scenarios as noted in the design docs.
