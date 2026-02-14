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

import detextive.exceptions as _exceptions


def test_000_imports( ):
    ''' Exception classes are accessible from main module. '''
    assert hasattr( _exceptions, 'BehaviorsInvalidity' )
    assert hasattr( _exceptions, 'CharsetDetectFailure' )
    assert hasattr( _exceptions, 'CharsetInferFailure' )
    assert hasattr( _exceptions, 'MimetypeDetectFailure' )
    assert hasattr( _exceptions, 'ContentDecodeFailure' )


def test_100_charset_detect_failure_without_location( ):
    ''' CharsetDetectFailure constructs correctly without location. '''
    exc = _exceptions.CharsetDetectFailure( )
    assert str( exc ) == "Could not detect character set for content."


def test_110_charset_detect_failure_with_string_location( ):
    ''' CharsetDetectFailure constructs correctly with string location. '''
    exc = _exceptions.CharsetDetectFailure( location = 'test.txt' )
    exc_str = str( exc )
    assert exc_str.startswith(
        "Could not detect character set for content at '" )
    assert exc_str.endswith( "'." )
    assert 'test.txt' in exc_str


def test_115_charset_detect_failure_with_path_location( ):
    ''' CharsetDetectFailure constructs correctly with Path location. '''
    location = Path( 'documents/file.txt' )
    exc = _exceptions.CharsetDetectFailure( location = location )
    exc_str = str( exc )
    assert exc_str.startswith(
        "Could not detect character set for content at '" )
    assert exc_str.endswith( "'." )
    # Check that location is included in the message
    assert 'documents' in exc_str and 'file.txt' in exc_str


def test_120_charset_infer_failure_without_location( ):
    ''' CharsetInferFailure constructs correctly without location. '''
    exc = _exceptions.CharsetInferFailure( )
    assert str( exc ) == "Could not infer character set for content."


def test_130_charset_infer_failure_with_string_location( ):
    ''' CharsetInferFailure constructs correctly with string location. '''
    exc = _exceptions.CharsetInferFailure( location = 'data.bin' )
    exc_str = str( exc )
    assert exc_str.startswith(
        "Could not infer character set for content at '" )
    assert exc_str.endswith( "'." )
    assert 'data.bin' in exc_str


def test_135_charset_infer_failure_with_path_location( ):
    ''' CharsetInferFailure constructs correctly with Path location. '''
    location = Path( 'data/test.dat' )
    exc = _exceptions.CharsetInferFailure( location = location )
    exc_str = str( exc )
    assert exc_str.startswith(
        "Could not infer character set for content at '" )
    assert exc_str.endswith( "'." )
    # Check that location components are included in the message
    assert 'data' in exc_str and 'test.dat' in exc_str


def test_140_mimetype_detect_failure_without_location( ):
    ''' MimetypeDetectFailure constructs correctly without location. '''
    exc = _exceptions.MimetypeDetectFailure( )
    assert str( exc ) == "Could not detect MIME type for content."


def test_150_mimetype_detect_failure_with_string_location( ):
    ''' MimetypeDetectFailure constructs correctly with string location. '''
    exc = _exceptions.MimetypeDetectFailure(
        location = 'file.unknown' )
    exc_str = str( exc )
    assert exc_str.startswith(
        "Could not detect MIME type for content at '" )
    assert exc_str.endswith( "'." )
    assert 'file.unknown' in exc_str


def test_155_mimetype_detect_failure_with_path_location( ):
    ''' MimetypeDetectFailure constructs correctly with Path location. '''
    location = Path( 'uploads/mystery.blob' )
    exc = _exceptions.MimetypeDetectFailure( location = location )
    exc_str = str( exc )
    assert exc_str.startswith(
        "Could not detect MIME type for content at '" )
    assert exc_str.endswith( "'." )
    # Check that location components are included in the message
    assert 'uploads' in exc_str and 'mystery.blob' in exc_str


def test_160_content_decode_failure_without_location( ):
    ''' ContentDecodeFailure constructs correctly without location. '''
    exc = _exceptions.ContentDecodeFailure( 'ascii' )
    expected = "Could not decode content with character sets 'ascii'."
    assert str( exc ) == expected


def test_170_content_decode_failure_with_string_location( ):
    ''' ContentDecodeFailure constructs correctly with string location. '''
    exc = _exceptions.ContentDecodeFailure(
        'latin-1', location = 'legacy.txt' )
    exc_str = str( exc )
    assert "Could not decode content at '" in exc_str
    assert "' with character sets 'latin-1'." in exc_str
    assert 'legacy.txt' in exc_str


def test_175_content_decode_failure_with_path_location( ):
    ''' ContentDecodeFailure constructs correctly with Path location. '''
    location = Path( 'files/old.doc' )
    exc = _exceptions.ContentDecodeFailure(
        'cp1252', location = location )
    exc_str = str( exc )
    assert "Could not decode content at '" in exc_str
    assert "' with character sets 'cp1252'." in exc_str
    # Check that location components are included in the message
    assert 'files' in exc_str and 'old.doc' in exc_str


def test_177_content_decode_impossibility_without_location( ):
    ''' ContentDecodeImpossibility constructs correctly without location. '''
    exc = _exceptions.ContentDecodeImpossibility( )
    expected = "Could not decode probable non-textual content."
    assert str( exc ) == expected


def test_178_content_decode_impossibility_with_string_location( ):
    ''' ContentDecodeImpossibility constructs with string location. '''
    exc = _exceptions.ContentDecodeImpossibility(
        location = 'test.bin' )
    exc_str = str( exc )
    assert exc_str.startswith(
        "Could not decode probable non-textual content at '" )
    assert exc_str.endswith( "'." )
    assert 'test.bin' in exc_str


def test_179_content_decode_impossibility_with_path_location( ):
    ''' ContentDecodeImpossibility constructs correctly with Path location. '''
    exc = _exceptions.ContentDecodeImpossibility(
        location = Path( 'data/binary.dat' ) )
    exc_str = str( exc )
    assert exc_str.startswith(
        "Could not decode probable non-textual content at '" )
    assert exc_str.endswith( "'." )
    # Check that location components are included in the message
    assert 'data' in exc_str and 'binary.dat' in exc_str


def test_180_exception_hierarchy_inheritance( ):
    ''' Exception hierarchy follows expected inheritance pattern. '''
    assert issubclass(
        _exceptions.Omnierror, _exceptions.Omniexception )
    assert issubclass( _exceptions.Omniexception, BaseException )
    assert issubclass( _exceptions.Omnierror, Exception )


def test_180_behaviors_invalidity_hierarchy_and_message( ):
    ''' BehaviorsInvalidity uses package family and type semantics. '''
    exc = _exceptions.BehaviorsInvalidity( 'charset_detect', 'a boolean' )
    assert isinstance( exc, _exceptions.Omnierror )
    assert isinstance( exc, TypeError )
    assert (
        str( exc )
        == "Behaviors attribute 'charset_detect' must be a boolean." )


def test_181_mimetype_infer_failure_without_location( ):
    ''' MimetypeInferFailure constructs correctly without location. '''
    exc = _exceptions.MimetypeInferFailure( )
    expected = "Could not infer MIME type for content."
    assert str( exc ) == expected


def test_182_mimetype_infer_failure_with_location( ):
    ''' MimetypeInferFailure constructs correctly with location. '''
    exc = _exceptions.MimetypeInferFailure( location = 'test.dat' )
    exc_str = str( exc )
    assert exc_str.startswith(
        "Could not infer MIME type for content at '" )
    assert exc_str.endswith( "'." )
    assert 'test.dat' in exc_str


def test_183_text_invalidity_with_location( ):
    ''' TextInvalidity constructs correctly with location. '''
    exc = _exceptions.TextInvalidity( location = 'invalid.txt' )
    exc_str = str( exc )
    assert exc_str.startswith( "Text is not valid at '" )
    assert exc_str.endswith( "'." )
    assert 'invalid.txt' in exc_str


def test_184_textual_mimetype_invalidity_without_location( ):
    ''' TextualMimetypeInvalidity constructs correctly without location. '''
    exc = _exceptions.TextualMimetypeInvalidity( 'image/png' )
    exc_str = str( exc )
    assert exc_str == "MIME type 'image/png' is not textual for content."


def test_187_textual_mimetype_invalidity_with_location( ):
    ''' TextualMimetypeInvalidity constructs correctly with location. '''
    exc = _exceptions.TextualMimetypeInvalidity(
        'application/pdf', location = 'document.pdf' )
    exc_str = str( exc )
    assert (
        "MIME type 'application/pdf' is not textual for content at '"
        in exc_str )
    assert exc_str.endswith( "'." )
    assert 'document.pdf' in exc_str


def test_190_package_exception_catching( ):
    ''' Package exceptions are catchable via base exception classes. '''
    exceptions = [
        _exceptions.CharsetDetectFailure( location = 'test.txt' ),
        _exceptions.CharsetInferFailure( location = 'test.bin' ),
        _exceptions.MimetypeDetectFailure( location = 'test.dat' ),
        _exceptions.ContentDecodeFailure(
            'utf-8', location = 'test.log' ),
    ]
    for exc in exceptions:
        assert isinstance( exc, _exceptions.Omnierror )
        assert isinstance( exc, _exceptions.Omniexception )
