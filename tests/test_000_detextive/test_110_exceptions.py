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


''' Exception classes location parameter handling is correct. '''


from pathlib import Path

import detextive


def test_000_imports( ):
    ''' Exception classes are accessible from main module. '''
    assert hasattr( detextive, 'exceptions' )
    assert hasattr( detextive.exceptions, 'CharsetDetectFailure' )
    assert hasattr( detextive.exceptions, 'CharsetInferFailure' )
    assert hasattr( detextive.exceptions, 'MimetypeDetectFailure' )
    assert hasattr( detextive.exceptions, 'ContentDecodeFailure' )


def test_100_charset_detect_failure_without_location( ):
    ''' CharsetDetectFailure constructs correctly without location. '''
    exc = detextive.exceptions.CharsetDetectFailure( )
    assert str( exc ) == "Could not detect character set for content."


def test_110_charset_detect_failure_with_string_location( ):
    ''' CharsetDetectFailure constructs correctly with string location. '''
    exc = detextive.exceptions.CharsetDetectFailure( location = 'test.txt' )
    expected = "Could not detect character set for content at 'test.txt'."
    assert str( exc ) == expected


def test_115_charset_detect_failure_with_path_location( ):
    ''' CharsetDetectFailure constructs correctly with Path location. '''
    location = Path( 'documents/file.txt' )
    exc = detextive.exceptions.CharsetDetectFailure( location = location )
    expected = (
        "Could not detect character set for content at 'documents/file.txt'." )
    assert str( exc ) == expected


def test_120_charset_infer_failure_without_location( ):
    ''' CharsetInferFailure constructs correctly without location. '''
    exc = detextive.exceptions.CharsetInferFailure( )
    assert str( exc ) == "Could not infer character set for content."


def test_130_charset_infer_failure_with_string_location( ):
    ''' CharsetInferFailure constructs correctly with string location. '''
    exc = detextive.exceptions.CharsetInferFailure( location = 'data.bin' )
    expected = "Could not infer character set for content at 'data.bin'."
    assert str( exc ) == expected


def test_135_charset_infer_failure_with_path_location( ):
    ''' CharsetInferFailure constructs correctly with Path location. '''
    location = Path( 'data/test.dat' )
    exc = detextive.exceptions.CharsetInferFailure( location = location )
    expected = "Could not infer character set for content at 'data/test.dat'."
    assert str( exc ) == expected


def test_140_mimetype_detect_failure_without_location( ):
    ''' MimetypeDetectFailure constructs correctly without location. '''
    exc = detextive.exceptions.MimetypeDetectFailure( )
    assert str( exc ) == "Could not detect MIME type for content."


def test_150_mimetype_detect_failure_with_string_location( ):
    ''' MimetypeDetectFailure constructs correctly with string location. '''
    exc = detextive.exceptions.MimetypeDetectFailure(
        location = 'file.unknown' )
    expected = "Could not detect MIME type for content at 'file.unknown'."
    assert str( exc ) == expected


def test_155_mimetype_detect_failure_with_path_location( ):
    ''' MimetypeDetectFailure constructs correctly with Path location. '''
    location = Path( 'uploads/mystery.blob' )
    exc = detextive.exceptions.MimetypeDetectFailure( location = location )
    expected = (
        "Could not detect MIME type for content at 'uploads/mystery.blob'." )
    assert str( exc ) == expected


def test_160_content_decode_failure_without_location( ):
    ''' ContentDecodeFailure constructs correctly without location. '''
    exc = detextive.exceptions.ContentDecodeFailure( 'ascii' )
    expected = "Could not decode content with character sets 'ascii'."
    assert str( exc ) == expected


def test_170_content_decode_failure_with_string_location( ):
    ''' ContentDecodeFailure constructs correctly with string location. '''
    exc = detextive.exceptions.ContentDecodeFailure(
        'latin-1', location = 'legacy.txt' )
    expected = (
        "Could not decode content at 'legacy.txt' with character sets "
        "'latin-1'." )
    assert str( exc ) == expected


def test_175_content_decode_failure_with_path_location( ):
    ''' ContentDecodeFailure constructs correctly with Path location. '''
    location = Path( 'files/old.doc' )
    exc = detextive.exceptions.ContentDecodeFailure(
        'cp1252', location = location )
    expected = (
        "Could not decode content at 'files/old.doc' with character sets "
        "'cp1252'." )
    assert str( exc ) == expected


def test_177_content_decode_impossibility_without_location( ):
    ''' ContentDecodeImpossibility constructs correctly without location. '''
    exc = detextive.exceptions.ContentDecodeImpossibility( )
    expected = "Could not decode probable non-textual content."
    assert str( exc ) == expected


def test_178_content_decode_impossibility_with_string_location( ):
    ''' ContentDecodeImpossibility constructs with string location. '''
    exc = detextive.exceptions.ContentDecodeImpossibility(
        location = 'test.bin' )
    expected = "Could not decode probable non-textual content at 'test.bin'."
    assert str( exc ) == expected


def test_179_content_decode_impossibility_with_path_location( ):
    ''' ContentDecodeImpossibility constructs correctly with Path location. '''
    exc = detextive.exceptions.ContentDecodeImpossibility(
        location = Path( 'data/binary.dat' ) )
    expected = (
        "Could not decode probable non-textual content at 'data/binary.dat'." )
    assert str( exc ) == expected


def test_180_exception_hierarchy_inheritance( ):
    ''' Exception hierarchy follows expected inheritance pattern. '''
    assert issubclass(
        detextive.exceptions.Omnierror, detextive.exceptions.Omniexception )
    assert issubclass( detextive.exceptions.Omniexception, BaseException )
    assert issubclass( detextive.exceptions.Omnierror, Exception )


def test_181_mimetype_infer_failure_without_location( ):
    ''' MimetypeInferFailure constructs correctly without location. '''
    exc = detextive.exceptions.MimetypeInferFailure( )
    expected = "Could not infer MIME type for content."
    assert str( exc ) == expected


def test_182_mimetype_infer_failure_with_location( ):
    ''' MimetypeInferFailure constructs correctly with location. '''
    exc = detextive.exceptions.MimetypeInferFailure( location = 'test.dat' )
    expected = "Could not infer MIME type for content at 'test.dat'."
    assert str( exc ) == expected


def test_183_text_invalidity_with_location( ):
    ''' TextInvalidity constructs correctly with location. '''
    exc = detextive.exceptions.TextInvalidity( location = 'invalid.txt' )
    expected = "Text is not valid at 'invalid.txt'."
    assert str( exc ) == expected


def test_184_textual_mimetype_invalidity_without_location( ):
    ''' TextualMimetypeInvalidity constructs correctly without location. '''
    exc = detextive.exceptions.TextualMimetypeInvalidity( 'image/png' )
    expected = "MIME type '{mimetype}' is not textual for content."
    assert str( exc ) == expected


def test_187_textual_mimetype_invalidity_with_location( ):
    ''' TextualMimetypeInvalidity constructs correctly with location. '''
    exc = detextive.exceptions.TextualMimetypeInvalidity(
        'application/pdf', location = 'document.pdf' )
    expected = (
        "MIME type '{mimetype}' is not textual for content "
        "at 'document.pdf'." )
    assert str( exc ) == expected


def test_190_package_exception_catching( ):
    ''' Package exceptions are catchable via base exception classes. '''
    exceptions = [
        detextive.exceptions.CharsetDetectFailure( location = 'test.txt' ),
        detextive.exceptions.CharsetInferFailure( location = 'test.bin' ),
        detextive.exceptions.MimetypeDetectFailure( location = 'test.dat' ),
        detextive.exceptions.ContentDecodeFailure(
            'utf-8', location = 'test.log' ),
    ]
    for exc in exceptions:
        assert isinstance( exc, detextive.exceptions.Omnierror )
        assert isinstance( exc, detextive.exceptions.Omniexception )