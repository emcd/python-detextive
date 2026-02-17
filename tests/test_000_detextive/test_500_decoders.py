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


''' Decoder fallback and error handling is correct. '''


import pytest

import detextive
import detextive.decoders as _decoders
import detextive.detectors as _detectors

from .patterns import (
    EMPTY_CONTENT,
    UTF8_WITH_BOM,
    UTF16_LE_NO_BOM,
    UTF16_WITH_BOM,
    UTF32_LE_NO_BOM,
    UTF32_WITH_BOM,
)

# Basic Tests (000-099): Module import and function accessibility

def test_000_imports( ):
    ''' Decode function is accessible from main module. '''
    assert hasattr( detextive, 'decode' )
    assert hasattr( detextive, 'decode_inform' )
    assert hasattr( _decoders, 'DecodeInformResult' )


# High-Level Decode Tests (100-199): decode function with various parameters

def test_100_decode_inference_failure_fallback_to_utf8_sig( ):
    ''' Inference failure falls back to utf-8-sig with confidence. '''
    # Force inference failure by using empty detector orders
    behaviors = detextive.Behaviors(
        charset_detectors_order = ( 'nonexistent-detector', ),
        mimetype_detectors_order = ( 'nonexistent-detector', ),
        charset_on_detect_failure = detextive.DetectFailureActions.Error,
        mimetype_on_detect_failure = detextive.DetectFailureActions.Error )
    utf8_content = b'Hello, world!'
    result = _decoders.decode(
        utf8_content, behaviors = behaviors )
    assert result == 'Hello, world!'


def test_110_decode_inference_failure_fallback_to_supplement( ):
    ''' Inference failure uses charset_supplement when provided. '''
    behaviors = detextive.Behaviors(
        charset_detectors_order = ( 'nonexistent-detector', ),
        mimetype_detectors_order = ( 'nonexistent-detector', ),
        charset_on_detect_failure = detextive.DetectFailureActions.Error,
        mimetype_on_detect_failure = detextive.DetectFailureActions.Error )
    content = b'Hello, world!'
    result = _decoders.decode(
        content, behaviors = behaviors, charset_supplement = 'ascii' )
    assert result == 'Hello, world!'


def test_120_decode_inform_reports_decode_and_metadata( ):
    ''' decode_inform returns text, charset, mimetype, and linesep. '''
    content = b'Hello,\nworld!\n'
    result = _decoders.decode_inform( content, location = 'test.txt' )
    assert result.text == 'Hello,\nworld!\n'
    assert result.charset.charset is not None
    assert result.mimetype.mimetype == 'text/plain'
    assert result.linesep == detextive.LineSeparators.LF


def test_130_decode_inform_honors_http_content_type( ):
    ''' decode_inform prefers HTTP Content-Type metadata when available. '''
    content = b'{"message": "hello"}'
    result = _decoders.decode_inform(
        content,
        http_content_type = 'application/json; charset=utf-8' )
    assert result.text == '{"message": "hello"}'
    assert result.charset.charset == 'utf-8'
    assert result.mimetype.mimetype == 'application/json'


def test_132_decode_inform_utf8_header_reports_bom_provenance( ):
    ''' UTF-8 reporting follows BOM provenance, independent of remove_bom. '''
    cases = (
        ( True, b'hello', 'hello', 'utf-8' ),
        ( True, UTF8_WITH_BOM, 'Hello, world!', 'utf-8-sig' ),
        ( False, b'hello', 'hello', 'utf-8' ),
        ( False, UTF8_WITH_BOM, '\ufeffHello, world!', 'utf-8-sig' ),
    )
    for remove_bom, content, expected_text, expected_charset in cases:
        behaviors = detextive.Behaviors( remove_bom = remove_bom )
        result = _decoders.decode_inform(
            content,
            behaviors = behaviors,
            http_content_type = 'text/plain; charset=utf-8' )
        assert result.text == expected_text
        assert result.charset.charset == expected_charset


def test_134_decode_inform_utf16_utf32_header_reports_bom_provenance( ):
    ''' UTF-16/32 reporting follows BOM provenance for header-guided decode.
    '''
    cases = (
        ( UTF16_LE_NO_BOM, 'text/plain; charset=utf-16-le', 'utf-16-le' ),
        ( UTF16_WITH_BOM, 'text/plain; charset=utf-16-le', 'utf-16' ),
        ( UTF32_LE_NO_BOM, 'text/plain; charset=utf-32-le', 'utf-32-le' ),
        ( UTF32_WITH_BOM, 'text/plain; charset=utf-32-le', 'utf-32' ),
    )
    for content, header, expected in cases:
        result = _decoders.decode_inform(
            content, http_content_type = header )
        assert result.charset.charset == expected


def test_136_decode_inform_strict_mode_rejects_bomless_generic_utf_header( ):
    ''' Strict mode rejects BOM-less generic UTF-16/32 from HTTP charset. '''
    cases = (
        ( UTF16_LE_NO_BOM, 'text/plain; charset=utf-16' ),
        ( UTF32_LE_NO_BOM, 'text/plain; charset=utf-32' ),
    )
    for content, header in cases:
        behaviors = detextive.Behaviors(
            charset_detect = False,
            trial_codecs = ( detextive.CodecSpecifiers.FromInference, ),
            utf_16_32_requires_byte_order = True )
        with pytest.raises( detextive.exceptions.ContentDecodeFailure ):
            _decoders.decode_inform(
                content, behaviors = behaviors, http_content_type = header )


def test_138_decode_inform_strict_mode_allows_explicit_utf_endianness_header(
):
    ''' Strict mode accepts BOM-less UTF-16/32 with explicit header charset.
    '''
    cases = (
        ( UTF16_LE_NO_BOM, 'text/plain; charset=utf-16-le', 'utf-16-le' ),
        ( UTF32_LE_NO_BOM, 'text/plain; charset=utf-32-le', 'utf-32-le' ),
    )
    for content, header, expected in cases:
        behaviors = detextive.Behaviors(
            charset_detect = False,
            trial_codecs = ( detextive.CodecSpecifiers.FromInference, ),
            utf_16_32_requires_byte_order = True )
        result = _decoders.decode_inform(
            content, behaviors = behaviors, http_content_type = header )
        assert result.text == 'Hello, world!'
        assert result.charset.charset == expected


def test_140_decode_inform_empty_content( ):
    ''' decode_inform returns deterministic metadata for empty content. '''
    result = _decoders.decode_inform( b'' )
    assert result.text == ''
    assert result.charset.charset == 'utf-8'
    assert result.charset.confidence == 1.0
    assert result.mimetype.mimetype == 'text/plain'
    assert result.linesep is None


def test_150_decode_inform_mimetype_inference_fallback( ):
    ''' Falls back to text/plain when MIME inference is unavailable. '''
    behaviors = detextive.Behaviors(
        mimetype_detect = False )
    result = _decoders.decode_inform( b'hello', behaviors = behaviors )
    assert result.mimetype.mimetype == 'text/plain'


def test_160_decode_inform_non_textual_mimetype_coerced( ):
    ''' Coerces non-textual location MIME to text/plain. '''
    result = _decoders.decode_inform(
        b'hello',
        location = 'artifact.png' )
    assert result.mimetype.mimetype == 'text/plain'


def test_170_decode_inform_non_textual_http_header_rejected( ):
    ''' Rejects non-textual HTTP Content-Type values with charset. '''
    with pytest.raises( detextive.exceptions.ContentDecodeImpossibility ):
        _decoders.decode_inform(
            b'hello',
            http_content_type = 'image/png; charset=utf-8' )


def test_180_decode_inform_header_charset_fallback_to_trials( ):
    ''' Falls back to standard decode trials when HTTP charset decode fails.'''
    result = _decoders.decode_inform(
        b'Caf\xc3\xa9',
        http_content_type = 'text/plain; charset=ascii' )
    assert result.text == 'Café'


def test_185_decode_inform_detector_non_textual_coerced_to_default( ):
    ''' Coerces non-textual detector MIME result to textual default. '''
    detector_name = 'test-decode-inform-image-png'
    def mimetype_png_detector( content, behaviors ):
        return detextive.core.MimetypeResult(
            mimetype = 'image/png', confidence = 0.9 )
    _detectors.mimetype_detectors[ detector_name ] = mimetype_png_detector
    behaviors = detextive.Behaviors(
        mimetype_detectors_order = ( detector_name, ) )
    result = _decoders.decode_inform( b'hello', behaviors = behaviors )
    assert result.mimetype.mimetype == 'text/plain'


def test_190_decode_validation_profile_parameters( ):
    ''' Validation profile parameters are applied correctly. '''
    content = b'\x00\x01\x02\xff'  # Binary content that fails text validation
    behaviors = detextive.Behaviors(
        text_validate = detextive.BehaviorTristate.Never )
    # Use http_content_type to override MIME detection (which would detect as
    # application/octet-stream and reject). This tests that text_validate=Never
    # allows content that would otherwise fail text validation.
    text = _decoders.decode(
        content, behaviors = behaviors,
        http_content_type = 'text/plain; charset=iso-8859-1' )
    assert text is not None  # Should succeed when validation is disabled


# Default Parameter Tests (200-299): Custom default values and behaviors

def test_200_decode_empty_content_returns_empty_string( ):
    ''' Empty content decoding returns empty string immediately. '''
    result = _decoders.decode( EMPTY_CONTENT )
    assert result == ''


def test_210_decode_no_default_fallback_on_detection_failure( ):
    ''' Decode does not use inference-style default charset fallbacks. '''
    behaviors = detextive.Behaviors(
        charset_detectors_order = ( 'nonexistent-detector', ),
        charset_on_detect_failure = detextive.DetectFailureActions.Default,
        trial_codecs = ( 'utf-8', ) )
    with pytest.raises( detextive.exceptions.ContentDecodeFailure ):
        _decoders.decode( b'\xa0', behaviors = behaviors )


# Error Handling Tests (400-499): Exception scenarios and recovery

def test_420_validation_failure_handling( ):
    ''' Validation failures are handled correctly during decoding. '''
    content = b'\x00\x01\x02\xff'  # Binary content that fails text validation
    behaviors = detextive.Behaviors(
        text_validate = detextive.BehaviorTristate.Always )
    # Use http_content_type to override MIME detection, so we can test that
    # text validation properly rejects the content
    with pytest.raises( detextive.exceptions.TextInvalidity ):
        _decoders.decode(
            content, behaviors = behaviors,
            http_content_type = 'text/plain; charset=iso-8859-1' )


def test_430_decode_ignores_mimetype_context( ):
    ''' Decode path remains charset-driven.

        Even with non-textual MIME signal.
    '''
    # Use a custom detector that returns charset=None
    def charset_none_detector( content, behaviors ):
        return detextive.core.CharsetResult( charset = None, confidence = 0.8 )
    def mimetype_png_detector( content, behaviors ):
        return detextive.core.MimetypeResult(
            mimetype = 'image/png', confidence = 0.8 )
    # Register custom detectors
    detextive.detectors.charset_detectors[ 'test-decode-charset-none' ] = (
        charset_none_detector )
    detextive.detectors.mimetype_detectors[ 'test-decode-mimetype-png' ] = (
        mimetype_png_detector )
    content = b'some binary data'
    # Configure behaviors to use only our custom detectors
    behaviors = detextive.Behaviors(
        charset_detectors_order = ( 'test-decode-charset-none', ),
        mimetype_detectors_order = ( 'test-decode-mimetype-png', ) )
    text = _decoders.decode( content, behaviors = behaviors )
    assert text == 'some binary data'
