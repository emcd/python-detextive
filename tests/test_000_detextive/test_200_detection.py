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


''' Detection functionality is correct. '''


from pathlib import Path
from unittest.mock import patch

import pytest

from . import PACKAGE_NAME, cache_import_module


@pytest.fixture
def detection_module( ):
    ''' Provides access to detection module. '''
    return cache_import_module( f"{PACKAGE_NAME}.detection" )


@pytest.fixture
def exceptions_module( ):
    ''' Provides access to exceptions module. '''
    return cache_import_module( f"{PACKAGE_NAME}.exceptions" )


# detect_charset tests (100-199)

def test_100_detect_charset_utf8_content( detection_module ):
    ''' Charset detection identifies UTF-8 content correctly. '''
    content = b'Hello, world! \xc3\xa9'  # UTF-8 with é
    result = detection_module.detect_charset( content )
    assert result == 'utf-8'


def test_110_detect_charset_empty_content( detection_module ):
    ''' Charset detection returns None for empty content. '''
    content = b''
    result = detection_module.detect_charset( content )
    assert result is None


def test_120_detect_charset_ascii_returns_utf8( detection_module ):
    ''' ASCII content returns utf-8 as superset. '''
    with patch( 'chardet.detect' ) as mock_chardet:
        mock_chardet.return_value = { 'encoding': 'ascii' }
        content = b'Simple ASCII text'
        result = detection_module.detect_charset( content )
        assert result == 'utf-8'


def test_130_detect_charset_false_positive_elimination( detection_module ):
    ''' MacRoman false positives are corrected to UTF-8. '''
    with patch( 'chardet.detect' ) as mock_chardet:
        mock_chardet.return_value = { 'encoding': 'MacRoman' }
        content = b'Valid UTF-8 content'  # Can decode as UTF-8
        result = detection_module.detect_charset( content )
        assert result == 'utf-8'


def test_140_detect_charset_non_utf8_content( detection_module ):
    ''' Non-UTF-8 content that fails UTF-8 decode returns detected charset. '''
    with patch( 'chardet.detect' ) as mock_chardet:
        mock_chardet.return_value = { 'encoding': 'iso-8859-1' }
        content = b'\xff\xfe'  # Cannot decode as UTF-8
        result = detection_module.detect_charset( content )
        assert result == 'iso-8859-1'


# detect_mimetype tests (200-299)

def test_200_detect_mimetype_magic_numbers( detection_module ):
    ''' MIME type detection works with magic numbers. '''
    jpeg_content = b'\xff\xd8\xff\xe0\x00\x10JFIF'
    result = detection_module.detect_mimetype( jpeg_content, 'test.jpg' )
    assert result == 'image/jpeg'


def test_210_detect_mimetype_extension_fallback( detection_module ):
    ''' Extension fallback works when magic detection fails. '''
    with patch( 'puremagic.from_string' ) as mock_puremagic:
        mock_puremagic.side_effect = ValueError( "No magic match" )
        content = b'Plain text content'
        result = detection_module.detect_mimetype( content, 'document.txt' )
        assert result == 'text/plain'


def test_220_detect_mimetype_puremagic_error_handling( detection_module ):
    ''' PureError from puremagic triggers extension fallback. '''
    with patch( 'puremagic.from_string' ) as mock_puremagic:
        # Import the actual PureError for realistic testing
        import puremagic
        mock_puremagic.side_effect = puremagic.PureError( "Test error" )
        content = b'Some content'
        result = detection_module.detect_mimetype( content, 'file.pdf' )
        assert result == 'application/pdf'


def test_230_detect_mimetype_path_object( detection_module ):
    ''' Path objects work as location parameters. '''
    content = b'Text content'
    location = Path( 'document.txt' )
    result = detection_module.detect_mimetype( content, location )
    assert result is not None  # Should detect something via extension


# detect_mimetype_and_charset tests (300-399)

def test_300_detect_both_mimetype_and_charset( detection_module ):
    ''' Both MIME type and charset detected successfully. '''
    content = b'<html><body>Hello</body></html>'
    mimetype, charset = detection_module.detect_mimetype_and_charset(
        content, 'page.html' )
    assert mimetype == 'text/html'
    assert charset == 'utf-8'


def test_310_mimetype_override_parameter( detection_module ):
    ''' Explicit mimetype override works correctly. '''
    content = b'Some content'
    mimetype, charset = detection_module.detect_mimetype_and_charset(
        content, 'unknown', mimetype = 'text/plain' )
    assert mimetype == 'text/plain'
    assert charset == 'utf-8'


def test_320_charset_override_parameter( detection_module ):
    ''' Explicit charset override works correctly. '''
    content = b'Some content'
    mimetype, charset = detection_module.detect_mimetype_and_charset(
        content, 'test.txt', charset = 'iso-8859-1' )
    assert mimetype == 'text/plain'
    assert charset == 'iso-8859-1'


def test_330_octet_stream_fallback( detection_module ):
    ''' Binary content with no detection falls back to octet-stream. '''
    with patch( 'puremagic.from_string' ) as mock_puremagic, \
         patch( 'mimetypes.guess_type' ) as mock_mimetypes, \
         patch( 'chardet.detect' ) as mock_chardet:

        mock_puremagic.side_effect = ValueError( "No magic" )
        mock_mimetypes.return_value = ( None, None )
        mock_chardet.return_value = { 'encoding': None }

        content = b'\x00\x01\x02\x03'
        mimetype, charset = detection_module.detect_mimetype_and_charset(
            content, 'binary_file' )
        assert mimetype == 'application/octet-stream'
        assert charset is None


def test_340_text_plain_fallback_with_charset( detection_module ):
    ''' Charset detected but no MIME type defaults to text/plain. '''
    with patch( 'puremagic.from_string' ) as mock_puremagic, \
         patch( 'mimetypes.guess_type' ) as mock_mimetypes:

        mock_puremagic.side_effect = ValueError( "No magic" )
        mock_mimetypes.return_value = ( None, None )

        content = b'Plain text without clear extension'
        mimetype, charset = detection_module.detect_mimetype_and_charset(
            content, 'unknown_file' )
        assert mimetype == 'text/plain'
        assert charset == 'utf-8'


def test_350_non_textual_mimetype_returns_without_charset( detection_module ):
    ''' Non-textual MIME type returns without charset. '''
    with patch( 'puremagic.from_string' ) as mock_puremagic:
        mock_puremagic.return_value = 'image/jpeg'

        content = b'\x00\x01\x02\x03'  # Binary content

        mimetype, charset = detection_module.detect_mimetype_and_charset(
            content, 'test.jpg' )
        assert mimetype == 'image/jpeg'
        assert charset is None


# is_textual_mimetype tests (400-499)

def test_400_text_prefix_detection( detection_module ):
    ''' Text/* prefixes are correctly identified as textual. '''
    assert detection_module.is_textual_mimetype( 'text/plain' ) is True
    assert detection_module.is_textual_mimetype( 'text/html' ) is True
    assert detection_module.is_textual_mimetype( 'text/x-custom' ) is True


def test_410_application_textual_types( detection_module ):
    ''' Known textual application types are identified. '''
    textual_types = [
        'application/json',
        'application/xml',
        'application/javascript',
        'application/yaml',
    ]
    for mimetype in textual_types:
        assert detection_module.is_textual_mimetype( mimetype ) is True


def test_420_textual_suffixes( detection_module ):
    ''' Textual suffixes are correctly identified. '''
    assert detection_module.is_textual_mimetype(
        'application/vnd.api+json' ) is True
    assert detection_module.is_textual_mimetype(
        'application/custom+xml' ) is True
    assert detection_module.is_textual_mimetype(
        'custom/type+yaml' ) is True
    assert detection_module.is_textual_mimetype(
        'custom/type+toml' ) is True


def test_430_non_textual_types( detection_module ):
    ''' Non-textual types return False. '''
    non_textual = [
        'image/jpeg',
        'video/mp4',
        'application/octet-stream',
        'audio/mpeg',
    ]
    for mimetype in non_textual:
        assert detection_module.is_textual_mimetype( mimetype ) is False


def test_440_empty_and_invalid_mimetypes( detection_module ):
    ''' Empty and malformed MIME types return False. '''
    assert detection_module.is_textual_mimetype( '' ) is False
    assert detection_module.is_textual_mimetype( 'invalid' ) is False


# is_reasonable_text_content tests (500-599)

def test_500_reasonable_text_content( detection_module ):
    ''' Normal text content is identified as reasonable. '''
    content = 'This is normal readable text with proper formatting.'
    assert detection_module.is_reasonable_text_content( content ) is True


def test_510_empty_content_rejection( detection_module ):
    ''' Empty content is rejected as unreasonable. '''
    assert detection_module.is_reasonable_text_content( '' ) is False


def test_520_excessive_control_characters( detection_module ):
    ''' Content with >10% control characters is rejected. '''
    content = '\x01\x02\x03text\x04\x05\x06'  # 6 control, 4 text = 60%
    assert detection_module.is_reasonable_text_content( content ) is False


def test_530_acceptable_whitespace( detection_module ):
    ''' Common whitespace characters are accepted. '''
    content = 'Line 1\n\tIndented line\rCarriage return line'
    assert detection_module.is_reasonable_text_content( content ) is True


def test_540_insufficient_printable_characters( detection_module ):
    ''' Content with <80% printable characters is rejected. '''
    # Create content with low printable ratio
    content = 'text' + '\x7f' * 20  # 4 printable, 20 non-printable = 17%
    assert detection_module.is_reasonable_text_content( content ) is False


# _validate_mimetype_with_trial_decode tests (600-699)
# These are tested indirectly through detect_mimetype_and_charset

def test_600_non_textual_mimetype_ignores_invalid_charset( detection_module ):
    ''' Non-textual MIME type ignores charset detection errors. '''
    with patch( 'puremagic.from_string' ) as mock_puremagic, \
         patch( 'chardet.detect' ) as mock_chardet:
        mock_puremagic.return_value = 'image/png'
        mock_chardet.return_value = { 'encoding': 'invalid-charset' }
        content = b'\x00\x01\x02'
        mimetype, charset = detection_module.detect_mimetype_and_charset(
            content, 'test.png' )
        assert mimetype == 'image/png'
        assert charset is None


def test_610_non_textual_mimetype_ignores_unreasonable_content(
        detection_module
):
    ''' Non-textual MIME type ignores content reasonableness. '''
    with patch( 'puremagic.from_string' ) as mock_puremagic, \
         patch( 'chardet.detect' ) as mock_chardet:
        mock_puremagic.return_value = 'image/png'
        mock_chardet.return_value = { 'encoding': 'utf-8' }
        # Content that decodes but fails reasonableness test
        content = ('\x01' * 50).encode( 'utf-8' )  # All control characters
        mimetype, charset = detection_module.detect_mimetype_and_charset(
            content, 'test.png' )
        assert mimetype == 'image/png'
        assert charset is None


def test_620_non_textual_mimetype_with_valid_charset( detection_module ):
    ''' Non-textual mimetype with valid charset and content succeeds. '''
    # Use explicit parameters to override detection and trigger line 128
    content = b'This is reasonable text content for testing purposes.'
    mimetype, charset = detection_module.detect_mimetype_and_charset(
        content, 'test.bin', mimetype='application/octet-stream',
        charset='utf-8' )
    assert mimetype == 'application/octet-stream'
    assert charset == 'utf-8'


def test_630_explicit_invalid_charset_raises_exception(
        detection_module, exceptions_module ):
    ''' Explicit invalid charset triggers TextualMimetypeInvalidity. '''
    content = b'Valid content'
    with pytest.raises( exceptions_module.TextualMimetypeInvalidity ):
        detection_module.detect_mimetype_and_charset(
            content, 'test.bin', mimetype='application/octet-stream',
            charset='invalid-charset' )


def test_640_text_plain_fallback_validation_failure( detection_module ):
    ''' Text/plain fallback invalid charset falls back to octet-stream. '''
    with patch( 'puremagic.from_string' ) as mock_puremagic, \
         patch( 'mimetypes.guess_type' ) as mock_mimetypes, \
         patch( 'chardet.detect' ) as mock_chardet:
        mock_puremagic.side_effect = ValueError( "No magic" )
        mock_mimetypes.return_value = ( None, None )
        mock_chardet.return_value = { 'encoding': 'ascii' }
        content = b'\xff\xfe'  # Invalid ASCII sequence
        mimetype, charset = detection_module.detect_mimetype_and_charset(
            content, 'unknown_file' )
        assert mimetype == 'application/octet-stream'
        assert charset is None


def test_650_unreasonable_content_validation_failure(
        detection_module, exceptions_module
):
    ''' Unreasonable content triggers TextualMimetypeInvalidity. '''
    content = ('\x01' * 100).encode( 'utf-8' )  # All control characters
    with pytest.raises( exceptions_module.TextualMimetypeInvalidity ):
        detection_module.detect_mimetype_and_charset(
            content, 'test.bin', mimetype='application/octet-stream',
            charset='utf-8' )
