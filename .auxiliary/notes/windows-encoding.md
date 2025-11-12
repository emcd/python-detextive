# Windows Doctest Encoding Issue

## Current Status

Python 3.11 on Windows doctest failure:
```
File "examples\basic-usage.rst", line 178, in BasicUsage
Failed example:
    text
Expected:
    'Caf� \u2605'
Got:
    'Café ★'
```

## Analysis

### Critical Clue
This test **previously passed** on Windows Python 3.10 and 3.11 before our charset validation fixes (commits 1aa0565, 2d98cec).

### What Changed

**Before our fixes:**
- Python 3.10 on Windows: `discover_os_charset_default()` used `sys.getfilesystemencoding()` → cp1252
- Python 3.11 on Windows: `discover_os_charset_default()` used `locale.getencoding()` → cp1252
- Charset detection confirmation tried OsDefault (cp1252) first
- Content `b'Caf\xc3\xa9 \xe2\x98\x85'` decoded with cp1252 → mojibake `'Caf� ★'`
- Mojibake matched doctest expectation → test passed (wrong result)

**After our fixes (commit 2d98cec):**
- Charset detection confirmation excludes OsDefault
- Tries only UserSupplement and FromInference
- chardet correctly detects content as utf-8
- Content decodes correctly as `'Café ★'`
- Doesn't match garbled expectation → test fails (correct result!)

### Why Python 3.10 Still Passes

Our fix in `_confirm_charset_detection()` works the same on both Python versions. Need to investigate why Python 3.10 still passes - possibly chardet behaves differently between versions?

### Question

**Should we fix the doctest expectation to match the correct output?**

This seems straightforward, but:
1. Why did the broken output match the doctest in the first place?
2. Is the doctest file encoding declaration being respected on Windows?
3. Could this be a Sphinx/doctest encoding configuration issue?

## Next Steps

1. Check if file has correct encoding declaration (has `.. -*- coding: utf-8 -*-`)
2. Verify what Python 3.10 on Windows actually produces now
3. Consider if we need Windows-specific doctest handling
4. Update doctest expectation if appropriate

## Related Files

- `documentation/examples/basic-usage.rst` line 178
- `sources/detextive/detectors.py` `_confirm_charset_detection()`
- Commits: 1aa0565 (MIME validation fix), 2d98cec (charset validation fix)
