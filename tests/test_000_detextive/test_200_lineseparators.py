# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Line separator detection and normalization tests. '''


import detextive
import detextive.lineseparators as _lineseparators


# Basic Tests (000-099): Enum structure and values validation

def test_000_imports( ):
    ''' Line separator functions are accessible from main module. '''
    assert hasattr( detextive, 'lineseparators' )


def test_010_enum_structure( ):
    ''' LineSeparators enum has expected values. '''
    assert hasattr( _lineseparators.LineSeparators, 'LF' )
    assert hasattr( _lineseparators.LineSeparators, 'CRLF' )
    assert hasattr( _lineseparators.LineSeparators, 'CR' )


def test_020_enum_values( ):
    ''' LineSeparators enum values are correct. '''
    assert _lineseparators.LineSeparators.LF.value == '\n'
    assert _lineseparators.LineSeparators.CRLF.value == '\r\n'
    assert _lineseparators.LineSeparators.CR.value == '\r'


# Detection Tests (100-199): Line separator detection from byte content

def test_100_detect_unix_lf_line_endings( ):
    ''' Unix LF line endings are identified correctly. '''
    content = b'line1\nline2\nline3'
    result = _lineseparators.LineSeparators.detect_bytes( content )
    assert result == _lineseparators.LineSeparators.LF


def test_110_detect_windows_crlf_line_endings( ):
    ''' Windows CRLF line endings are identified correctly. '''
    content = b'line1\r\nline2\r\nline3'
    result = _lineseparators.LineSeparators.detect_bytes( content )
    assert result == _lineseparators.LineSeparators.CRLF


def test_120_detect_mac_cr_line_endings( ):
    ''' Classic Mac CR line endings are identified correctly. '''
    content = b'line1\rline2\rline3'
    result = _lineseparators.LineSeparators.detect_bytes( content )
    assert result == _lineseparators.LineSeparators.CR


def test_130_detect_content_double_cr( ):
    ''' Content with double CR triggers early return. '''
    content = b'text\r\rmore text'  # CR followed by CR
    result = _lineseparators.LineSeparators.detect_bytes( content )
    assert result == _lineseparators.LineSeparators.CR


def test_140_detect_content_cr_followed_by_char( ):
    ''' Content with CR followed by non-LF character triggers early return. '''
    content = b'text\rx'  # CR followed by regular character
    result = _lineseparators.LineSeparators.detect_bytes( content )
    assert result == _lineseparators.LineSeparators.CR


def test_150_detect_text_double_cr( ):
    ''' Text with double CR triggers early return. '''
    text = 'text\r\rmore text'  # CR followed by CR
    result = _lineseparators.LineSeparators.detect_text( text )
    assert result == _lineseparators.LineSeparators.CR


def test_160_detect_text_cr_followed_by_char( ):
    ''' Text with CR followed by non-LF character triggers early return. '''
    text = 'text\rx'  # CR followed by regular character
    result = _lineseparators.LineSeparators.detect_text( text )
    assert result == _lineseparators.LineSeparators.CR


def test_170_detect_mixed_line_endings_first_wins( ):
    ''' Mixed line endings return first type encountered. '''
    content = b'line1\nline2\r\nline3'  # LF first, then CRLF
    result = _lineseparators.LineSeparators.detect_bytes( content )
    assert result == _lineseparators.LineSeparators.LF


def test_180_detect_no_line_separators_returns_none( ):
    ''' Content without line separators returns None. '''
    content = b'single line without separators'
    result = _lineseparators.LineSeparators.detect_bytes( content )
    assert result is None


def test_190_detect_empty_content_returns_none( ):
    ''' Empty content produces no line separator result. '''
    content = b''
    result = _lineseparators.LineSeparators.detect_bytes( content )
    assert result is None


# Normalization Tests (200-299): normalize_universal and individual enum
# normalize methods

def test_200_normalize_universal_all_to_lf( ):
    ''' Universal normalization converts all endings to LF. '''
    content_crlf = 'line1\r\nline2\r\nline3'
    content_cr = 'line1\rline2\rline3'
    expected = 'line1\nline2\nline3'
    normalize_fn = _lineseparators.LineSeparators.normalize_universal
    result_crlf = normalize_fn( content_crlf )
    result_cr = normalize_fn( content_cr )
    assert result_crlf == expected
    assert result_cr == expected


def test_210_normalize_universal_no_endings_unchanged( ):
    ''' Universal normalization preserves content without endings. '''
    content = 'single line without endings'
    normalize_fn = _lineseparators.LineSeparators.normalize_universal
    result = normalize_fn( content )
    assert result == content


def test_220_normalize_universal_empty_content( ):
    ''' Universal normalization handles empty content correctly. '''
    content = ''
    normalize_fn = _lineseparators.LineSeparators.normalize_universal
    result = normalize_fn( content )
    assert result == content


def test_230_normalize_lf_returns_unchanged( ):
    ''' LF line separator normalize returns content unchanged. '''
    content = 'line1\nline2\nline3'
    result = _lineseparators.LineSeparators.LF.normalize( content )
    assert result == content


def test_240_normalize_crlf_converts_to_lf( ):
    ''' CRLF line separator normalize converts to LF. '''
    content = 'line1\r\nline2\r\nline3'
    result = _lineseparators.LineSeparators.CRLF.normalize( content )
    assert result == 'line1\nline2\nline3'


def test_250_normalize_cr_converts_to_lf( ):
    ''' CR line separators convert to LF during normalization. '''
    content = 'line1\rline2\rline3'
    result = _lineseparators.LineSeparators.CR.normalize( content )
    assert result == 'line1\nline2\nline3'


def test_260_normalize_preserve_already_normalized( ):
    ''' Already normalized content remains unchanged. '''
    content = 'line1\nline2\nline3'
    normalize_fn = _lineseparators.LineSeparators.normalize_universal
    result = normalize_fn( content )
    assert result == content


# Platform Conversion Tests (300-399): nativize method behavior per
# platform

def test_300_nativize_lf_to_platform_specific( ):
    ''' Unix LF to platform-specific conversion. '''
    content = 'line1\nline2\nline3'
    result = _lineseparators.LineSeparators.LF.nativize( content )
    # Result depends on platform, but should be consistent
    assert isinstance( result, str )
    assert all( line in result for line in ['line1', 'line2', 'line3'] )


def test_310_nativize_crlf_to_platform_specific( ):
    ''' Windows CRLF to platform-specific conversion. '''
    content = 'line1\nline2\nline3'
    result = _lineseparators.LineSeparators.CRLF.nativize( content )
    # Should convert LF to CRLF
    assert result == 'line1\r\nline2\r\nline3'


def test_320_nativize_cr_to_platform_specific( ):
    ''' Classic Mac CR to platform-specific conversion. '''
    content = 'line1\nline2\nline3'
    result = _lineseparators.LineSeparators.CR.nativize( content )
    # Should convert LF to CR
    assert result == 'line1\rline2\rline3'


def test_330_nativize_no_line_endings( ):
    ''' Content without line endings in nativize. '''
    content = 'single line without endings'
    result = _lineseparators.LineSeparators.LF.nativize( content )
    assert result == content


# Edge Case Tests (400-499): Complex content scenarios

def test_400_very_long_content_mixed_endings( ):
    ''' Very long content with mixed endings. '''
    content = 'line1\n' * 1000 + 'line2\r\n' * 1000 + 'line3\r' * 1000
    result = _lineseparators.LineSeparators.detect_text( content )
    # First ending wins
    assert result == _lineseparators.LineSeparators.LF


def test_410_consecutive_line_separators( ):
    ''' Consecutive line separators. '''
    content = b'line1\n\n\nline2'
    result = _lineseparators.LineSeparators.detect_bytes( content )
    assert result == _lineseparators.LineSeparators.LF


def test_420_line_separators_at_boundaries( ):
    ''' Line separators at content boundaries. '''
    content_start = b'\nline1\nline2'
    content_end = b'line1\nline2\n'
    content_both = b'\nline1\nline2\n'
    detect_fn = _lineseparators.LineSeparators.detect_bytes
    result_start = detect_fn( content_start )
    result_end = detect_fn( content_end )
    result_both = detect_fn( content_both )
    expected = _lineseparators.LineSeparators.LF
    assert result_start == expected
    assert result_end == expected
    assert result_both == expected


def test_430_integer_sequence_input( ):
    ''' Integer sequences are processed correctly. '''
    content = [ord('l'), ord('i'), ord('n'), ord('e'), ord('\n'), ord('2')]
    detect_fn = _lineseparators.LineSeparators.detect_bytes
    result = detect_fn( content )
    assert result == _lineseparators.LineSeparators.LF


def test_440_detection_limit_parameter_behavior( ):
    ''' Detection limit parameter controls search scope. '''
    content = b'line1\nline2\r\nline3'  # LF first, CRLF later
    # Test with limit that only sees first line ending
    detect_fn = _lineseparators.LineSeparators.detect_bytes
    result = detect_fn( content, limit=10 )
    assert result == _lineseparators.LineSeparators.LF


# Windows Compatibility Tests (500-599): Cross-platform behavior

def test_500_crlf_detection_accuracy_windows( ):
    ''' CRLF detection accuracy on Windows. '''
    content = b'line1\r\nline2\r\nline3\r\n'
    detect_fn = _lineseparators.LineSeparators.detect_bytes
    result = detect_fn( content )
    assert result == _lineseparators.LineSeparators.CRLF


def test_510_cross_platform_consistency( ):
    ''' Cross-platform nativize behavior consistency. '''
    content = 'line1\nline2\nline3'
    # All enum values should produce consistent results
    separators = _lineseparators.LineSeparators
    lf_result = separators.LF.nativize( content )
    crlf_result = separators.CRLF.nativize( content )
    cr_result = separators.CR.nativize( content )
    # Results should be predictable
    assert lf_result == content
    assert crlf_result == 'line1\r\nline2\r\nline3'
    assert cr_result == 'line1\rline2\rline3'


def test_520_large_content_handling( ):
    ''' Large content handling (Cygwin buffer considerations). '''
    # Create content larger than typical buffer sizes
    large_content = b'line\n' * 10000
    detect_fn = _lineseparators.LineSeparators.detect_bytes
    result = detect_fn( large_content )
    assert result == _lineseparators.LineSeparators.LF