#!/usr/bin/env python3
# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-
# ruff: noqa

"""
Compare chardet vs charset-normalizer detection behavior.

Evaluates both detectors on various byte patterns to determine:
1. Which normalizes to more standard/practical encodings
2. Detection confidence levels
3. Handling of edge cases (binary, ambiguous, empty)
4. Performance characteristics
"""

import time
from typing import Any

try:
    import chardet
except ImportError:
    chardet = None

try:
    import charset_normalizer
except ImportError:
    charset_normalizer = None


# Test patterns covering various scenarios
TEST_PATTERNS = {
    # UTF-8 variants
    'utf8_basic': b'Hello, world!',
    'utf8_accents': b'Caf\xc3\xa9 \xc3\xa0 Paris',
    'utf8_emoji': b'Hello \xf0\x9f\x91\x8b world \xf0\x9f\x8c\x8d',
    'utf8_cjk': b'\xe4\xb8\xad\xe6\x96\x87',  # Chinese characters
    'utf8_arabic': b'\xd8\xa7\xd9\x84\xd8\xb9\xd8\xb1\xd8\xa8\xd9\x8a\xd8\xa9',
    'utf8_mixed': b'Mix: \xc3\xa9 \xe2\x98\x85 \xf0\x9f\x8e\x89',

    # UTF-16 with BOM
    'utf16_le_bom': b'\xff\xfeH\x00e\x00l\x00l\x00o\x00',
    'utf16_be_bom': b'\xfe\xff\x00H\x00e\x00l\x00l\x00o',

    # ISO-8859-1 / Latin-1
    'latin1': b'Caf\xe9 \xe0 Paris',  # Valid Latin-1, invalid UTF-8
    'latin1_extended': b'\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9',

    # Windows-1252
    'cp1252': b'Smart quotes: \x93Hello\x94 \x96 Em dash',

    # ASCII
    'ascii': b'Plain ASCII text without special characters',
    'ascii_with_newlines': b'Line 1\nLine 2\r\nLine 3\rLine 4',

    # ISO-8859-2 (Central European)
    'latin2': b'\xb1\xb6\xbe',  # Polish characters

    # KOI8-R (Russian)
    'koi8r': b'\xf0\xd2\xc9\xd7\xc5\xd4',  # Cyrillic

    # Shift-JIS (Japanese)
    'shiftjis': b'\x82\xb1\x82\xf1\x82\xc9\x82\xbf\x82\xcd',

    # Edge cases
    'empty': b'',
    'single_byte': b'A',
    'null_bytes': b'\x00\x00\x00\x00',
    'high_bytes': b'\xff\xfe\xfd\xfc\xfb',

    # Binary-like patterns
    'binary_png': b'\x89PNG\r\n\x1a\n',
    'binary_pdf': b'%PDF-1.4',
    'binary_zip': b'PK\x03\x04',
    'binary_random': bytes(range(0, 256, 17)),  # 0, 17, 34, ...

    # Ambiguous cases (valid in multiple encodings)
    'ambiguous_simple': b'test',  # ASCII, UTF-8, Latin-1, etc.
    'ambiguous_accents': b'\xe9\xe8\xe0',  # Valid Latin-1 and Windows-1252
}


def detect_with_chardet(content: bytes) -> dict[str, Any]:
    """Run chardet detection."""
    if chardet is None:
        return {'error': 'chardet not installed'}

    start = time.perf_counter()
    result = chardet.detect(content)
    elapsed = time.perf_counter() - start

    return {
        'encoding': result.get('encoding'),
        'confidence': result.get('confidence'),
        'language': result.get('language'),
        'time_ms': elapsed * 1000,
    }


def detect_with_charset_normalizer(content: bytes) -> dict[str, Any]:
    """Run charset-normalizer detection."""
    if charset_normalizer is None:
        return {'error': 'charset-normalizer not installed'}

    start = time.perf_counter()
    results = charset_normalizer.from_bytes(content)
    best = results.best()
    elapsed = time.perf_counter() - start

    if best is None:
        return {
            'encoding': None,
            'confidence': 0.0,
            'time_ms': elapsed * 1000,
        }

    return {
        'encoding': best.encoding,
        'confidence': best.coherence,  # 0.0-1.0 coherence score
        'language': getattr(best, 'language', None),
        'time_ms': elapsed * 1000,
        'coherence': best.coherence,
    }


def format_result(name: str, content: bytes, chardet_result: dict,
                  normalizer_result: dict) -> str:
    """Format comparison results for display."""
    lines = []
    lines.append(f"\n{'=' * 70}")
    lines.append(f"Pattern: {name}")
    lines.append(f"Content: {content[:50]!r}" +
                 ('...' if len(content) > 50 else ''))
    lines.append(f"Length: {len(content)} bytes")
    lines.append('-' * 70)

    # chardet results
    lines.append("chardet:")
    if 'error' in chardet_result:
        lines.append(f"  ERROR: {chardet_result['error']}")
    else:
        lines.append(f"  Encoding:   {chardet_result['encoding']}")
        lines.append(f"  Confidence: {chardet_result['confidence']:.2f}")
        if chardet_result.get('language'):
            lines.append(f"  Language:   {chardet_result['language']}")
        lines.append(f"  Time:       {chardet_result['time_ms']:.3f} ms")

    lines.append("")

    # charset-normalizer results
    lines.append("charset-normalizer:")
    if 'error' in normalizer_result:
        lines.append(f"  ERROR: {normalizer_result['error']}")
    else:
        lines.append(f"  Encoding:   {normalizer_result['encoding']}")
        lines.append(f"  Confidence: {normalizer_result['confidence']:.2f}")
        if normalizer_result.get('language'):
            lines.append(f"  Language:   {normalizer_result['language']}")
        if normalizer_result.get('coherence') is not None:
            lines.append(f"  Coherence:  {normalizer_result['coherence']:.2f}")
        lines.append(f"  Time:       {normalizer_result['time_ms']:.3f} ms")

    # Comparison
    lines.append('-' * 70)
    if ('error' not in chardet_result and 'error' not in normalizer_result):
        enc1 = chardet_result['encoding']
        enc2 = normalizer_result['encoding']
        if enc1 and enc2:
            enc1_norm = enc1.lower().replace('-', '').replace('_', '')
            enc2_norm = enc2.lower().replace('-', '').replace('_', '')
            if enc1_norm == enc2_norm:
                lines.append("✓ MATCH: Both detected same encoding")
            else:
                lines.append(f"✗ DIFFER: {enc1} vs {enc2}")

                # Try to decode with each to see which works better
                try:
                    text1 = content.decode(enc1)
                    lines.append(f"  chardet decode: OK ({len(text1)} chars)")
                except Exception as e:
                    lines.append(f"  chardet decode: FAIL ({type(e).__name__})")

                try:
                    text2 = content.decode(enc2)
                    lines.append(f"  normalizer decode: OK ({len(text2)} chars)")
                except Exception as e:
                    lines.append(f"  normalizer decode: FAIL ({type(e).__name__})")
        elif enc1 and not enc2:
            lines.append("chardet detected, normalizer returned None")
        elif enc2 and not enc1:
            lines.append("normalizer detected, chardet returned None")
        else:
            lines.append("Both returned None")

    return '\n'.join(lines)


def main():
    """Run comparison on all test patterns."""
    print("=" * 70)
    print("Charset Detector Comparison: chardet vs charset-normalizer")
    print("=" * 70)

    if chardet is None:
        print("\n⚠ WARNING: chardet is not installed")
    else:
        print(f"\nchardet version: {getattr(chardet, '__version__', 'unknown')}")

    if charset_normalizer is None:
        print("⚠ WARNING: charset-normalizer is not installed")
    else:
        print(f"charset-normalizer version: "
              f"{getattr(charset_normalizer, '__version__', 'unknown')}")

    # Summary statistics
    matches = 0
    differs = 0
    chardet_faster = 0
    normalizer_faster = 0

    for name, content in TEST_PATTERNS.items():
        chardet_result = detect_with_chardet(content)
        normalizer_result = detect_with_charset_normalizer(content)

        print(format_result(name, content, chardet_result, normalizer_result))

        # Track statistics
        if ('error' not in chardet_result and
            'error' not in normalizer_result and
            chardet_result['encoding'] and
            normalizer_result['encoding']):
            enc1 = chardet_result['encoding'].lower().replace('-', '').replace('_', '')
            enc2 = normalizer_result['encoding'].lower().replace('-', '').replace('_', '')
            if enc1 == enc2:
                matches += 1
            else:
                differs += 1

            if chardet_result['time_ms'] < normalizer_result['time_ms']:
                chardet_faster += 1
            else:
                normalizer_faster += 1

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total patterns tested: {len(TEST_PATTERNS)}")
    print(f"Detections match:      {matches}")
    print(f"Detections differ:     {differs}")
    print(f"chardet faster:        {chardet_faster}")
    print(f"normalizer faster:     {normalizer_faster}")
    print("=" * 70)


if __name__ == '__main__':
    main()
