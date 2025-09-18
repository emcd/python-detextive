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


''' Line separator detection edge cases. '''


import detextive


def test_000_imports( ):
    ''' Line separator functions are accessible from main module. '''
    assert hasattr( detextive, 'lineseparators' )


def test_100_detect_no_line_separators_returns_none( ):
    ''' Content without line separators returns None. '''
    content = b'single line without separators'
    result = detextive.lineseparators.LineSeparators.detect_bytes( content )
    assert result is None


def test_110_normalize_lf_returns_unchanged( ):
    ''' LF line separator normalize returns content unchanged. '''
    content = 'line1\nline2\nline3'
    result = detextive.lineseparators.LineSeparators.LF.normalize( content )
    assert result == content


def test_120_normalize_crlf_converts_to_lf( ):
    ''' CRLF line separator normalize converts to LF. '''
    content = 'line1\r\nline2\r\nline3'
    result = detextive.lineseparators.LineSeparators.CRLF.normalize( content )
    assert result == 'line1\nline2\nline3'