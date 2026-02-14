#!/usr/bin/env python3
# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-
# ruff: noqa

"""
Test charset normalization behavior.

Specifically evaluates whether charset-normalizer prefers standard/practical
encodings over obscure ones, compared to chardet.

This addresses the concern: does charset-normalizer actually "normalize" to
useful encodings like UTF-8, or does it detect rare encodings like MacRoman?
"""

try:
    import chardet
except ImportError:
    chardet = None

try:
    import charset_normalizer
except ImportError:
    charset_normalizer = None


# Standard/preferred encodings (in priority order)
STANDARD_ENCODINGS = [
    'utf-8',
    'ascii',
    'iso-8859-1',  # Latin-1
    'windows-1252',  # Most common Windows encoding
    'iso-8859-2',  # Central European
    'iso-8859-15',  # Latin-9 (Euro sign)
]

# Obscure/problematic encodings that should be avoided
OBSCURE_ENCODINGS = [
    'MacRoman',
    'MacCyrillic',
    'TIS-620',  # Thai
    'IBM855',
    'IBM866',
]


def normalize_encoding_name(encoding: str | None) -> str:
    """Normalize encoding name for comparison."""
    if not encoding:
        return ''
    return encoding.lower().replace('-', '').replace('_', '')


def classify_encoding(encoding: str | None) -> str:
    """Classify encoding as standard, obscure, or unknown."""
    if not encoding:
        return 'none'

    normalized = normalize_encoding_name(encoding)

    # Check standard encodings
    for std in STANDARD_ENCODINGS:
        if normalize_encoding_name(std) == normalized:
            return f'standard:{std}'

    # Check obscure encodings
    for obs in OBSCURE_ENCODINGS:
        if normalize_encoding_name(obs) == normalized:
            return f'obscure:{obs}'

    return f'other:{encoding}'


def test_pattern(name: str, content: bytes) -> dict:
    """Test a pattern with both detectors and classify results."""
    result = {
        'name': name,
        'content': content[:50],
        'length': len(content),
    }

    # chardet
    if chardet:
        detection = chardet.detect(content)
        result['chardet'] = {
            'encoding': detection.get('encoding'),
            'confidence': detection.get('confidence'),
            'classification': classify_encoding(detection.get('encoding')),
        }
    else:
        result['chardet'] = {'encoding': None, 'error': 'not installed'}

    # charset-normalizer
    if charset_normalizer:
        results = charset_normalizer.from_bytes(content)
        best = results.best()
        if best:
            result['normalizer'] = {
                'encoding': best.encoding,
                'confidence': best.coherence,  # 0.0-1.0 coherence score
                'classification': classify_encoding(best.encoding),
            }
        else:
            result['normalizer'] = {
                'encoding': None,
                'confidence': 0.0,
                'classification': 'none',
            }
    else:
        result['normalizer'] = {'encoding': None, 'error': 'not installed'}

    return result


# Test cases specifically designed to trigger different detections
NORMALIZATION_TESTS = {
    # UTF-8 content that might be misdetected
    'utf8_short': b'Caf\xc3\xa9',
    'utf8_medium': b'Caf\xc3\xa9 \xc3\xa0 Paris avec \xc3\xa9l\xc3\xa9gance',
    'utf8_long': (b'The quick brown fox jumps over the lazy dog. '
                  b'Caf\xc3\xa9, na\xc3\xafve, \xc3\xa9l\xc3\xa8ve. ' * 3),

    # ASCII-safe content (should stay ASCII, not escalate to UTF-8)
    'pure_ascii': b'Hello world, this is plain ASCII text.',
    'ascii_multiline': b'Line 1\nLine 2\nLine 3\nPlain text.',

    # Latin-1 vs UTF-8 ambiguity
    'latin1_french': b'Caf\xe9 \xe0 Paris',  # Valid Latin-1, invalid UTF-8
    'latin1_spanish': b'Ma\xf1ana espa\xf1ol',

    # Windows-1252 specific characters
    'cp1252_quotes': b'It\x92s a \x93smart\x94 test',
    'cp1252_euro': b'Price: \x80100',  # Euro sign in Windows-1252

    # Content that could be MacRoman (test if normalizer avoids it)
    'potential_macroman': b'Caf\x8e',  # é in MacRoman

    # ISO-8859-2 (Central European)
    'latin2_polish': b'\xb3\xf3d\xbc',  # Polish: łódź

    # Mixed valid encodings (which is preferred?)
    'multi_valid_1': b'test',  # Valid in many encodings
    'multi_valid_2': b'\xe9\xe8\xe0\xe7',  # Valid Latin-1/Win1252

    # Edge case: could be UTF-8 or 8-bit
    'ambiguous_high': b'\xc3\xa9\xc3\xa8',  # Valid UTF-8 or Latin-1

    # Realistic web content (should prefer UTF-8)
    'web_html': b'<html><body>Caf\xc3\xa9</body></html>',
    'web_json': b'{"name": "Caf\xc3\xa9", "city": "Paris"}',

    # Realistic file content
    'text_file': b'# Comment\n\nCaf\xc3\xa9 notes\n\nMore text here.\n',
}


def main():
    """Run normalization behavior tests."""
    print("=" * 70)
    print("Charset Normalization Behavior Test")
    print("=" * 70)

    if chardet is None:
        print("\n⚠ WARNING: chardet is not installed\n")
    if charset_normalizer is None:
        print("⚠ WARNING: charset-normalizer is not installed\n")

    results = []
    for name, content in NORMALIZATION_TESTS.items():
        result = test_pattern(name, content)
        results.append(result)

    # Print detailed results
    for result in results:
        print(f"\n{'=' * 70}")
        print(f"Test: {result['name']}")
        print(f"Content: {result['content']!r}...")
        print(f"Length: {result['length']} bytes")
        print('-' * 70)

        if 'error' not in result['chardet']:
            cd = result['chardet']
            print(f"chardet:           {cd['encoding']:20} "
                  f"[{cd['confidence']:.2f}] {cd['classification']}")

        if 'error' not in result['normalizer']:
            cn = result['normalizer']
            print(f"charset-normalizer: {cn['encoding']:20} "
                  f"[{cn['confidence']:.2f}] {cn['classification']}")

        # Analysis
        if ('error' not in result['chardet'] and
            'error' not in result['normalizer']):
            cd_class = result['chardet']['classification']
            cn_class = result['normalizer']['classification']

            if cd_class.startswith('obscure') and cn_class.startswith('standard'):
                print("\n✓ BETTER: normalizer chose standard over obscure")
            elif cd_class.startswith('standard') and cn_class.startswith('obscure'):
                print("\n✗ WORSE: normalizer chose obscure over standard")
            elif cd_class == cn_class:
                print("\n= SAME: Both chose same classification")
            else:
                print(f"\n? DIFFERENT: {cd_class} vs {cn_class}")

    # Summary statistics
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if chardet and charset_normalizer:
        chardet_standard = sum(1 for r in results
                               if r['chardet']['classification'].startswith('standard'))
        chardet_obscure = sum(1 for r in results
                              if r['chardet']['classification'].startswith('obscure'))

        norm_standard = sum(1 for r in results
                           if r['normalizer']['classification'].startswith('standard'))
        norm_obscure = sum(1 for r in results
                          if r['normalizer']['classification'].startswith('obscure'))

        print(f"Total tests: {len(results)}")
        print()
        print(f"chardet - Standard encodings:  {chardet_standard}")
        print(f"chardet - Obscure encodings:   {chardet_obscure}")
        print()
        print(f"normalizer - Standard:         {norm_standard}")
        print(f"normalizer - Obscure:          {norm_obscure}")
        print()

        if norm_standard > chardet_standard:
            print("✓ charset-normalizer prefers standard encodings more")
        elif norm_standard < chardet_standard:
            print("✗ chardet prefers standard encodings more")
        else:
            print("= Both prefer standard encodings equally")

        if norm_obscure < chardet_obscure:
            print("✓ charset-normalizer avoids obscure encodings more")
        elif norm_obscure > chardet_obscure:
            print("✗ charset-normalizer uses obscure encodings more")
        else:
            print("= Both use obscure encodings equally")

    print("=" * 70)


if __name__ == '__main__':
    main()
