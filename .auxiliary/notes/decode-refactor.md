# Decode Function Refactor

## Current State (v3 branch)

This note captures the historical rationale that led to the current decode
simplification and trial-order model now implemented on `decode-refactor`.

## Core Insight

Charset detection remains heuristic and context dependent. In ambiguous cases,
there is no universally reliable algorithmic shortcut. Simpler, deterministic
behavior with explicit user controls is easier to reason about and maintain.

## Practical Lessons

1. UTF and 8-bit cross-decoding can both produce plausible-looking mojibake.
2. Header and detector signals can help, but neither is perfectly reliable.
3. Platform defaults differ (notably Windows shell contexts), so trial ordering
   must avoid over-trusting local defaults.
4. Validation remains essential because successful decode does not imply
   textual validity.
5. Historical observation from this refactor cycle: CP1252 has undefined byte
   mappings (e.g., 0x81, 0x8d, 0x8f, 0x90, 0x9d), so it is not a total
   byte-to-codepoint mapping.

## Implemented Direction

1. Simplified `decode()` internals to use `charsets.attempt_decodes(...)`
   directly with a validator hook.
2. Removed bespoke decode helper pipeline in `decoders.py`.
3. Kept explicit HTTP header handling path first when `http_content_type` is
   supplied.
4. Updated default trial order to prioritize user/context and UTF-8 ahead of
   OS defaults:
   - `UserSupplement`
   - `'utf-8'`
   - `FromInference`
   - `OsDefault`
   - `PythonDefault`
5. Preserved behavior that `decode()` is not gated by MIME inference in its
   normal path.

## Test/Doc Alignment Completed

1. Test expectations updated for BOM-aware normalized charset names where
   applicable (`utf-8-sig`).
2. Inference tests aligned to normalized codec naming (`iso8859-1` form).
3. Decoder behavior tests updated to reflect charset-driven decode semantics.
4. Doctests updated for the same behavior shifts.

## Deferred Follow-ups

1. Continue API-shape work for single-call metadata-rich decode
   (`decode_inform` direction).
2. Keep detector-confidence refinements scoped separately from core decode
   simplification.
