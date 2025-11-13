#!/usr/bin/env python3
# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-
# ruff: noqa

"""
Test decode accuracy: which detector produces better text for decoding?

Creates test content in known encodings, then tests whether each detector
correctly identifies the encoding and produces the expected decoded text.
"""

try:
    import chardet
except ImportError:
    chardet = None

try:
    import charset_normalizer
except ImportError:
    charset_normalizer = None


# Test cases: (text, encoding, description)
TEST_CASES = [
    # UTF-8 cases
    ('Hello, world!', 'utf-8', 'Simple ASCII-compatible UTF-8'),
    ('Café à Paris', 'utf-8', 'UTF-8 with accents'),
    ('Hello 👋 world 🌍', 'utf-8', 'UTF-8 with emoji'),
    ('中文测试', 'utf-8', 'UTF-8 Chinese'),
    ('Привет мир', 'utf-8', 'UTF-8 Cyrillic'),
    ('مرحبا', 'utf-8', 'UTF-8 Arabic'),
    ('こんにちは世界', 'utf-8', 'UTF-8 Japanese'),

    # Latin-1 / ISO-8859-1
    ('Café à Paris', 'iso-8859-1', 'Latin-1 French'),
    ('Mañana español', 'iso-8859-1', 'Latin-1 Spanish'),
    ('Ñoño', 'iso-8859-1', 'Latin-1 with ñ'),

    # Windows-1252
    ('It\u2019s a \u201csmart\u201d test', 'windows-1252', 'Win1252 smart quotes'),
    ('Price: \u20ac100', 'windows-1252', 'Win1252 Euro sign'),
    ('Em\u2014dash test', 'windows-1252', 'Win1252 em dash'),

    # ISO-8859-2 (Central European)
    ('Zażółć gęślą jaźń', 'iso-8859-2', 'Polish text'),
    ('Příliš žluťoučký', 'iso-8859-2', 'Czech text'),

    # Multiple lines / structured text
    ('Line 1: Café\nLine 2: naïve\nLine 3: élève', 'utf-8',
     'Multi-line UTF-8'),
    ('# Comment\n\nCafé notes\n\nMore text.', 'utf-8',
     'UTF-8 with structure'),

    # Realistic content
    ('<html><body><p>Café</p></body></html>', 'utf-8', 'HTML with UTF-8'),
    ('{"name": "Café", "city": "Paris"}', 'utf-8', 'JSON with UTF-8'),
    ('name,city\n"Café","Paris"\n', 'utf-8', 'CSV with UTF-8'),
]


def test_detection(original_text: str, encoding: str,
                   description: str) -> dict:
    """Test detection and decoding for a known text/encoding pair."""
    # Encode to bytes
    try:
        content = original_text.encode(encoding)
    except (UnicodeEncodeError, LookupError) as e:
        return {
            'error': f'Failed to encode: {e}',
            'description': description,
        }

    result = {
        'description': description,
        'original_text': original_text,
        'true_encoding': encoding,
        'content_length': len(content),
    }

    # Test chardet
    if chardet:
        detection = chardet.detect(content)
        detected_encoding = detection.get('encoding')
        confidence = detection.get('confidence')

        result['chardet'] = {
            'detected': detected_encoding,
            'confidence': confidence,
        }

        if detected_encoding:
            try:
                decoded_text = content.decode(detected_encoding)
                result['chardet']['decoded_text'] = decoded_text
                result['chardet']['text_matches'] = (decoded_text == original_text)
                result['chardet']['text_length'] = len(decoded_text)
            except (UnicodeDecodeError, LookupError) as e:
                result['chardet']['decode_error'] = str(e)
        else:
            result['chardet']['decoded_text'] = None
    else:
        result['chardet'] = {'error': 'not installed'}

    # Test charset-normalizer
    if charset_normalizer:
        results = charset_normalizer.from_bytes(content)
        best = results.best()

        if best:
            detected_encoding = best.encoding
            confidence = best.coherence  # 0.0-1.0 coherence score

            result['normalizer'] = {
                'detected': detected_encoding,
                'confidence': confidence,
            }

            try:
                decoded_text = content.decode(detected_encoding)
                result['normalizer']['decoded_text'] = decoded_text
                result['normalizer']['text_matches'] = (decoded_text == original_text)
                result['normalizer']['text_length'] = len(decoded_text)
            except (UnicodeDecodeError, LookupError) as e:
                result['normalizer']['decode_error'] = str(e)
        else:
            result['normalizer'] = {
                'detected': None,
                'confidence': 0.0,
                'decoded_text': None,
            }
    else:
        result['normalizer'] = {'error': 'not installed'}

    return result


def normalize_encoding_name(encoding: str) -> str:
    """Normalize encoding name for comparison."""
    return encoding.lower().replace('-', '').replace('_', '')


def main():
    """Run decode accuracy tests."""
    print("=" * 70)
    print("Decode Accuracy Test: chardet vs charset-normalizer")
    print("=" * 70)
    print("\nTests whether each detector correctly identifies encodings")
    print("and produces the expected decoded text.\n")

    if chardet is None:
        print("⚠ WARNING: chardet is not installed\n")
    if charset_normalizer is None:
        print("⚠ WARNING: charset-normalizer is not installed\n")

    results = []
    for text, encoding, description in TEST_CASES:
        result = test_detection(text, encoding, description)
        results.append(result)

    # Print detailed results
    for i, result in enumerate(results, 1):
        print(f"\n{'=' * 70}")
        print(f"Test {i}: {result['description']}")
        print(f"True encoding: {result['true_encoding']}")
        print(f"Original text: {result['original_text']!r}")

        if 'error' in result:
            print(f"ERROR: {result['error']}")
            continue

        print(f"Content length: {result['content_length']} bytes")
        print('-' * 70)

        # chardet results
        if 'error' not in result['chardet']:
            cd = result['chardet']
            print(f"chardet:")
            print(f"  Detected:   {cd['detected']}")
            print(f"  Confidence: {cd['confidence']:.2f}")

            if 'decode_error' in cd:
                print(f"  Decode:     FAILED - {cd['decode_error']}")
            elif cd['decoded_text'] is None:
                print(f"  Decode:     No encoding detected")
            else:
                match_str = "✓ MATCH" if cd['text_matches'] else "✗ DIFFER"
                print(f"  Decode:     {match_str}")
                print(f"  Result:     {cd['decoded_text']!r}")
                if not cd['text_matches']:
                    print(f"  Length:     {cd['text_length']} chars "
                          f"(expected {len(result['original_text'])})")

        # charset-normalizer results
        if 'error' not in result['normalizer']:
            cn = result['normalizer']
            print(f"\ncharset-normalizer:")
            print(f"  Detected:   {cn['detected']}")
            print(f"  Confidence: {cn['confidence']:.2f}")

            if 'decode_error' in cn:
                print(f"  Decode:     FAILED - {cn['decode_error']}")
            elif cn['decoded_text'] is None:
                print(f"  Decode:     No encoding detected")
            else:
                match_str = "✓ MATCH" if cn['text_matches'] else "✗ DIFFER"
                print(f"  Decode:     {match_str}")
                print(f"  Result:     {cn['decoded_text']!r}")
                if not cn['text_matches']:
                    print(f"  Length:     {cn['text_length']} chars "
                          f"(expected {len(result['original_text'])})")

        # Comparison
        if ('error' not in result['chardet'] and
            'error' not in result['normalizer']):
            print('-' * 70)

            cd_match = result['chardet'].get('text_matches', False)
            cn_match = result['normalizer'].get('text_matches', False)

            if cd_match and cn_match:
                print("✓ Both produced correct text")
            elif cn_match and not cd_match:
                print("✓ BETTER: normalizer correct, chardet wrong")
            elif cd_match and not cn_match:
                print("✗ WORSE: chardet correct, normalizer wrong")
            else:
                print("✗ Both produced incorrect text")

    # Summary statistics
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if chardet and charset_normalizer:
        total = len([r for r in results if 'error' not in r])

        cd_correct = sum(1 for r in results
                        if 'error' not in r
                        and 'error' not in r['chardet']
                        and r['chardet'].get('text_matches', False))
        cd_failed = sum(1 for r in results
                       if 'error' not in r
                       and 'error' not in r['chardet']
                       and 'decode_error' in r['chardet'])

        cn_correct = sum(1 for r in results
                        if 'error' not in r
                        and 'error' not in r['normalizer']
                        and r['normalizer'].get('text_matches', False))
        cn_failed = sum(1 for r in results
                       if 'error' not in r
                       and 'error' not in r['normalizer']
                       and 'decode_error' in r['normalizer'])

        print(f"Total valid tests: {total}")
        print()
        print(f"chardet:")
        print(f"  Correct:      {cd_correct}/{total} "
              f"({cd_correct/total*100:.1f}%)")
        print(f"  Decode failed: {cd_failed}")
        print()
        print(f"charset-normalizer:")
        print(f"  Correct:      {cn_correct}/{total} "
              f"({cn_correct/total*100:.1f}%)")
        print(f"  Decode failed: {cn_failed}")
        print()

        if cn_correct > cd_correct:
            diff = cn_correct - cd_correct
            print(f"✓ charset-normalizer is more accurate (+{diff} correct)")
        elif cd_correct > cn_correct:
            diff = cd_correct - cn_correct
            print(f"✗ chardet is more accurate (+{diff} correct)")
        else:
            print("= Both have equal accuracy")

    print("=" * 70)


if __name__ == '__main__':
    main()
