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


''' LineSeparators functionality is correct. '''


import pytest

from .__ import PACKAGE_NAME, cache_import_module


@pytest.fixture
def lineseparators_module( ):
    ''' Provides access to lineseparators module. '''
    return cache_import_module( f"{PACKAGE_NAME}.lineseparators" )


# LineSeparators enum basic tests (100-199)

def test_100_enum_members_exist( lineseparators_module ):
    ''' Enum contains expected members with correct values. '''
    LineSeparators = lineseparators_module.LineSeparators
    assert hasattr( LineSeparators, 'CR' )
    assert hasattr( LineSeparators, 'CRLF' )
    assert hasattr( LineSeparators, 'LF' )


def test_110_enum_string_representations( lineseparators_module ):
    ''' Enum members have proper string representations. '''
    LineSeparators = lineseparators_module.LineSeparators
    assert str( LineSeparators.CR ) == 'LineSeparators.CR'
    assert str( LineSeparators.CRLF ) == 'LineSeparators.CRLF'
    assert str( LineSeparators.LF ) == 'LineSeparators.LF'


def test_120_enum_comparison_and_hashing( lineseparators_module ):
    ''' Enum members support comparison and hashing. '''
    LineSeparators = lineseparators_module.LineSeparators
    # Test equality
    assert LineSeparators.CR == LineSeparators.CR
    assert LineSeparators.CR != LineSeparators.LF
    # Test hashability
    enum_set = { LineSeparators.CR, LineSeparators.CRLF, LineSeparators.LF }
    assert len( enum_set ) == 3


# detect_bytes method tests (200-299)

def test_200_detect_lf_line_endings( lineseparators_module ):
    ''' Unix LF line endings are detected correctly. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = b'line1\nline2\nline3'
    result = LineSeparators.detect_bytes( content )
    assert result == LineSeparators.LF


def test_210_detect_crlf_line_endings( lineseparators_module ):
    ''' Windows CRLF line endings are detected correctly. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = b'line1\r\nline2\r\nline3'
    result = LineSeparators.detect_bytes( content )
    assert result == LineSeparators.CRLF


def test_220_detect_cr_line_endings( lineseparators_module ):
    ''' Legacy CR line endings are detected correctly. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = b'line1\rline2\rline3'
    result = LineSeparators.detect_bytes( content )
    assert result == LineSeparators.CR


def test_230_no_line_endings_detected( lineseparators_module ):
    ''' Content without line endings returns None. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = b'single line without separators'
    result = LineSeparators.detect_bytes( content )
    assert result is None


def test_240_empty_content_detection( lineseparators_module ):
    ''' Empty content returns None. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = b''
    result = LineSeparators.detect_bytes( content )
    assert result is None


def test_250_mixed_line_endings_first_wins( lineseparators_module ):
    ''' Mixed line endings - first encountered type wins. '''
    LineSeparators = lineseparators_module.LineSeparators
    # LF appears first
    content = b'line1\nline2\r\nline3\rline4'
    result = LineSeparators.detect_bytes( content )
    assert result == LineSeparators.LF


def test_260_cr_followed_by_other_characters( lineseparators_module ):
    ''' CR followed by non-LF characters is detected as CR. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = b'line1\rX\rline2'  # CR followed by 'X', not LF
    result = LineSeparators.detect_bytes( content )
    assert result == LineSeparators.CR


def test_270_consecutive_cr_detection( lineseparators_module ):
    ''' Consecutive CR characters are detected as CR. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = b'line1\r\rline2'  # Two consecutive CRs
    result = LineSeparators.detect_bytes( content )
    assert result == LineSeparators.CR


def test_280_int_sequence_input( lineseparators_module ):
    ''' Integer sequence input is handled correctly. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = [ ord( c ) for c in 'line1\nline2' ]  # List of integers
    result = LineSeparators.detect_bytes( content )
    assert result == LineSeparators.LF


# normalize_universal method tests (300-399)

def test_300_normalize_crlf_to_lf( lineseparators_module ):
    ''' CRLF sequences are normalized to LF. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = 'Line 1\r\nLine 2\r\nLine 3'
    result = LineSeparators.normalize_universal( content )
    assert result == 'Line 1\nLine 2\nLine 3'


def test_310_normalize_cr_to_lf( lineseparators_module ):
    ''' CR sequences are normalized to LF. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = 'Line 1\rLine 2\rLine 3'
    result = LineSeparators.normalize_universal( content )
    assert result == 'Line 1\nLine 2\nLine 3'


def test_320_normalize_mixed_line_endings( lineseparators_module ):
    ''' Mixed line ending types are all normalized to LF. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = 'Line 1\r\nLine 2\rLine 3\nLine 4'
    result = LineSeparators.normalize_universal( content )
    assert result == 'Line 1\nLine 2\nLine 3\nLine 4'


def test_330_normalize_already_lf_unchanged( lineseparators_module ):
    ''' Content with only LF endings remains unchanged. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = 'Line 1\nLine 2\nLine 3'
    result = LineSeparators.normalize_universal( content )
    assert result == 'Line 1\nLine 2\nLine 3'


def test_340_normalize_no_line_endings_unchanged( lineseparators_module ):
    ''' Content without line endings remains unchanged. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = 'Single line without separators'
    result = LineSeparators.normalize_universal( content )
    assert result == 'Single line without separators'


def test_350_normalize_empty_string( lineseparators_module ):
    ''' Empty string normalization returns empty string. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = ''
    result = LineSeparators.normalize_universal( content )
    assert result == ''


# normalize method tests (400-499)

def test_400_cr_normalize_to_lf( lineseparators_module ):
    ''' CR enum member normalizes CR to LF. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = 'Line 1\rLine 2\rLine 3'
    result = LineSeparators.CR.normalize( content )
    assert result == 'Line 1\nLine 2\nLine 3'


def test_410_crlf_normalize_to_lf( lineseparators_module ):
    ''' CRLF enum member normalizes CRLF to LF. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = 'Line 1\r\nLine 2\r\nLine 3'
    result = LineSeparators.CRLF.normalize( content )
    assert result == 'Line 1\nLine 2\nLine 3'


def test_420_lf_normalize_unchanged( lineseparators_module ):
    ''' LF enum member returns content unchanged. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = 'Line 1\nLine 2\nLine 3'
    result = LineSeparators.LF.normalize( content )
    assert result == 'Line 1\nLine 2\nLine 3'


def test_430_normalize_multiple_occurrences( lineseparators_module ):
    ''' Multiple separator occurrences are all normalized. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = 'A\r\nB\r\nC\r\nD'  # Multiple CRLF
    result = LineSeparators.CRLF.normalize( content )
    assert result == 'A\nB\nC\nD'


def test_440_normalize_no_matching_separators( lineseparators_module ):
    ''' Content without matching separators remains unchanged. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = 'Line 1\nLine 2\nLine 3'  # Has LF, not CR
    result = LineSeparators.CR.normalize( content )
    assert result == 'Line 1\nLine 2\nLine 3'


# nativize method tests (500-599)

def test_500_cr_nativize_lf_to_cr( lineseparators_module ):
    ''' CR enum member converts LF to CR. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = 'Line 1\nLine 2\nLine 3'
    result = LineSeparators.CR.nativize( content )
    assert result == 'Line 1\rLine 2\rLine 3'


def test_510_crlf_nativize_lf_to_crlf( lineseparators_module ):
    ''' CRLF enum member converts LF to CRLF. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = 'Line 1\nLine 2\nLine 3'
    result = LineSeparators.CRLF.nativize( content )
    assert result == 'Line 1\r\nLine 2\r\nLine 3'


def test_520_lf_nativize_unchanged( lineseparators_module ):
    ''' LF enum member returns content unchanged. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = 'Line 1\nLine 2\nLine 3'
    result = LineSeparators.LF.nativize( content )
    assert result == 'Line 1\nLine 2\nLine 3'


def test_530_nativize_multiple_line_endings( lineseparators_module ):
    ''' Multiple LF occurrences are all converted. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = 'A\nB\nC\nD'
    result = LineSeparators.CRLF.nativize( content )
    assert result == 'A\r\nB\r\nC\r\nD'


def test_540_nativize_no_line_endings( lineseparators_module ):
    ''' Content without LF remains unchanged during nativization. '''
    LineSeparators = lineseparators_module.LineSeparators
    content = 'Single line without LF'
    result = LineSeparators.CRLF.nativize( content )
    assert result == 'Single line without LF'
