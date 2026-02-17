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


''' Enhanced inference functions and context handling. '''


import pytest

import detextive
import detextive.__ as _internals
import detextive.inference as _inference

from .patterns import (
    EMPTY_CONTENT,
    UTF16_LE_NO_BOM,
    UTF16_WITH_BOM,
    UTF32_LE_NO_BOM,
    UTF32_WITH_BOM,
    UTF8_BASIC,
    UTF8_WITH_BOM,
)


# Basic Tests (000-099): Module import and function accessibility

def test_000_imports( ):
    ''' Inference functions are accessible from main module. '''
    assert hasattr( detextive, 'inference' )


# Charset Inference Tests (100-199): infer_charset with HTTP headers

def test_100_infer_charset_string_function( ):
    ''' Infer charset returns string instead of result object. '''
    charset = _inference.infer_charset( UTF8_BASIC )
    assert isinstance( charset, str )
    assert charset is not None


def test_110_infer_charset_confidence_empty_content( ):
    ''' Empty content inference returns UTF-8 with full confidence. '''
    result = _inference.infer_charset_confidence( EMPTY_CONTENT )
    assert result.charset == 'utf-8'
    assert result.confidence == 1.0


def test_120_infer_charset_confidence_http_content_type_parsing( ):
    ''' HTTP content type parsing extracts charset from header. '''
    content = UTF8_BASIC
    http_content_type = 'text/plain; charset=iso-8859-1'
    result = _inference.infer_charset_confidence(
        content, http_content_type = http_content_type )
    assert result.charset == 'iso8859-1'


def test_125_infer_charset_httpct_honored_with_detect_enabled( ):
    ''' Header charset is honored when charset detection is enabled. '''
    content = 'Café'.encode( 'iso-8859-1' )
    behaviors = detextive.Behaviors(
        charset_detect = True,
        charset_detectors_order = ( 'nonexistent-detector', ),
        charset_on_detect_failure = detextive.DetectFailureActions.Error )
    result = _inference.infer_charset_confidence(
        content,
        behaviors = behaviors,
        http_content_type = 'text/plain; charset=iso-8859-1' )
    assert result.charset == 'iso8859-1'


def test_130_infer_charset_confidence_detection_fallback( ):
    ''' Falls back to detection when no other methods work. '''
    behaviors = detextive.Behaviors(
        charset_detect = True )
    result = _inference.infer_charset_confidence(
        UTF8_BASIC, behaviors = behaviors )
    assert result.charset is not None
    assert result.confidence >= 0.0


def test_140_infer_charset_confidence_failure_when_no_detection( ):
    ''' Raises CharsetInferFailure when no detection methods available. '''
    behaviors = detextive.Behaviors(
        charset_detect = False,
        charset_detectors_order = ( 'nonexistent-detector', ),
        charset_on_detect_failure = detextive.DetectFailureActions.Error )
    with pytest.raises( detextive.exceptions.CharsetInferFailure ):
        _inference.infer_charset_confidence(
            UTF8_BASIC, behaviors = behaviors )


def test_150_charset_result_early_return( ):
    ''' Charset inference early return when result is valid. '''
    content = b'test content with charset info'
    charset_result = _inference.infer_charset_confidence(
        content,
        behaviors = detextive.Behaviors(
            charset_detect = True ),
        http_content_type = 'text/plain; charset=utf-8' )
    assert hasattr( charset_result, 'charset' )
    assert charset_result.charset is not None


def test_160_mimetype_result_absent_branch( ):
    ''' HTTP parsing returns absent mimetype_result. '''
    content = b'test content'
    result = _inference.infer_charset_confidence(
        content,
        http_content_type = '; charset=utf-8' )
    assert result.charset == 'utf-8'


def test_170_charset_result_absent_no_early_return( ):
    ''' HTTP parsing with absent charset_result continues to detection. '''
    content = b'test content'
    result = _inference.infer_charset_confidence(
        content,
        http_content_type = 'text/plain' )
    assert hasattr( result, 'charset' )




# Combined Inference Tests (200-299): infer_mimetype_charset functions

def test_200_http_content_type_parsing_success( ):
    ''' HTTP Content-Type parsing succeeds with valid headers. '''
    utf8_content = 'Hello, world!'.encode( 'utf-8' )
    behaviors = detextive.Behaviors(
        mimetype_on_detect_failure = detextive.DetectFailureActions.Default,
        charset_on_detect_failure = detextive.DetectFailureActions.Default )
    mimetype_result, charset_result = (
        _inference.infer_mimetype_charset_confidence(
            utf8_content, behaviors = behaviors,
            http_content_type = 'text/plain; charset=utf-8' ) )
    assert mimetype_result.mimetype == 'text/plain'
    assert charset_result.charset == 'utf-8'


def test_205_httpct_honored_with_both_detect_enabled( ):
    ''' Header parse is honored when both detect behaviors are enabled. '''
    content = UTF8_BASIC
    behaviors = detextive.Behaviors(
        charset_detect = True,
        mimetype_detect = True,
        charset_detectors_order = ( 'nonexistent-detector', ),
        mimetype_detectors_order = ( 'nonexistent-detector', ),
        charset_on_detect_failure = detextive.DetectFailureActions.Error,
        mimetype_on_detect_failure = detextive.DetectFailureActions.Error )
    mimetype_result, charset_result = (
        _inference.infer_mimetype_charset_confidence(
            content,
            behaviors = behaviors,
            http_content_type = 'text/plain; charset=utf-8' ) )
    assert mimetype_result.mimetype == 'text/plain'
    assert charset_result.charset == 'utf-8'


def test_206_httpct_utf8_charset_reports_bom_provenance( ):
    ''' HTTP charset validation reports UTF-8 BOM provenance. '''
    cases = (
        ( True, UTF8_BASIC, 'utf-8' ),
        ( True, UTF8_WITH_BOM, 'utf-8-sig' ),
        ( False, UTF8_BASIC, 'utf-8' ),
        ( False, UTF8_WITH_BOM, 'utf-8-sig' ),
    )
    for remove_bom, content, expected in cases:
        behaviors = detextive.Behaviors( remove_bom = remove_bom )
        _, charset_result = _inference.infer_mimetype_charset_confidence(
            content,
            behaviors = behaviors,
            http_content_type = 'text/plain; charset=utf-8' )
        assert charset_result.charset == expected


def test_207_httpct_utf16_utf32_report_bom_provenance( ):
    ''' HTTP charset validation reports UTF-16/32 BOM provenance. '''
    cases = (
        ( UTF16_LE_NO_BOM, 'text/plain; charset=utf-16-le', 'utf-16-le' ),
        ( UTF16_WITH_BOM, 'text/plain; charset=utf-16-le', 'utf-16' ),
        ( UTF32_LE_NO_BOM, 'text/plain; charset=utf-32-le', 'utf-32-le' ),
        ( UTF32_WITH_BOM, 'text/plain; charset=utf-32-le', 'utf-32' ),
    )
    for content, header, expected in cases:
        _, charset_result = _inference.infer_mimetype_charset_confidence(
            content, http_content_type = header )
        assert charset_result.charset == expected


def test_210_location_based_mimetype_inference( ):
    ''' Location-based mimetype inference when HTTP parsing absent. '''
    utf8_content = 'Hello, world!'.encode( 'utf-8' )
    behaviors = detextive.Behaviors(
        mimetype_on_detect_failure = detextive.DetectFailureActions.Default )
    mimetype_result, _ = _inference.infer_mimetype_charset_confidence(
        utf8_content, behaviors = behaviors,
        location = 'test.txt' )
    assert mimetype_result.mimetype == 'text/plain'
    assert mimetype_result.confidence == 0.9


def test_220_inference_failure_scenarios( ):
    ''' Inference failure scenarios raise appropriate exceptions. '''
    content = b'test content'
    behaviors = detextive.Behaviors(
        charset_detectors_order = ( ),
        charset_on_detect_failure = detextive.DetectFailureActions.Error )
    with pytest.raises( detextive.exceptions.CharsetDetectFailure ):
        _inference.infer_mimetype_charset_confidence(
            content, behaviors = behaviors )
    behaviors = detextive.Behaviors(
        mimetype_detectors_order = ( ),
        mimetype_on_detect_failure = detextive.DetectFailureActions.Error )
    with pytest.raises( detextive.exceptions.MimetypeDetectFailure ):
        _inference.infer_mimetype_charset_confidence(
            content, behaviors = behaviors )


def test_230_mimetype_detection_disabled( ):
    ''' Disabled MIME detection bypasses detector execution. '''
    content = b'test content'
    behaviors = detextive.Behaviors(
        mimetype_detect = False,
        charset_on_detect_failure = detextive.DetectFailureActions.Default,
        mimetype_on_detect_failure = detextive.DetectFailureActions.Default )
    mimetype_result, _ = _inference.infer_mimetype_charset_confidence(
        content, behaviors = behaviors,
        http_content_type = 'text/plain; charset=utf-8' )
    assert mimetype_result.mimetype == 'text/plain'


def test_240_http_validation_charset_edge_cases( ):
    ''' HTTP validation handles charset absent and None cases. '''
    content = b'test content'
    behaviors = detextive.Behaviors( )
    mimetype_result, _ = _inference.infer_mimetype_charset_confidence(
        content, behaviors = behaviors,
        http_content_type = 'image/png' )
    assert mimetype_result.mimetype == 'image/png'


def test_250_http_validation_mimetype_absent( ):
    ''' HTTP validation when mimetype parsing yields absent result. '''
    content = b'test content'
    behaviors = detextive.Behaviors(
        charset_on_detect_failure = detextive.DetectFailureActions.Default,
        mimetype_on_detect_failure = detextive.DetectFailureActions.Default )
    _, charset_result = _inference.infer_mimetype_charset_confidence(
        content, behaviors = behaviors,
        http_content_type = 'invalid-content-type' )
    assert charset_result is not None


def test_260_charset_infer_failure_exception( ):
    ''' CharsetInferFailure raised when charset inference completely fails. '''
    content = b'test content'
    behaviors = detextive.Behaviors(
        charset_detect = False,
        charset_on_detect_failure = detextive.DetectFailureActions.Error )
    with pytest.raises( detextive.exceptions.CharsetInferFailure ):
        _inference.infer_mimetype_charset_confidence(
            content,
            behaviors = behaviors,
            charset_default = '' )


def test_270_mimetype_infer_failure_exception( ):
    ''' MimetypeInferFailure raised when mimetype inference fails. '''
    content = b'test content'
    behaviors = detextive.Behaviors(
        mimetype_detect = False,
        mimetype_on_detect_failure = detextive.DetectFailureActions.Error )
    with pytest.raises( detextive.exceptions.MimetypeInferFailure ):
        _inference.infer_mimetype_charset_confidence(
            content,
            behaviors = behaviors,
            mimetype_default = '' )


def test_280_should_parse_false_branch( ):
    ''' Absent HTTP header uses regular detection paths. '''
    content = b'test content'
    behaviors = detextive.Behaviors(
        charset_detect = True,
        mimetype_detect = True )
    result = _inference.infer_mimetype_charset_confidence(
        content,
        behaviors = behaviors,
        http_content_type = _internals.absent )
    assert result[0] is not None
    assert result[1] is not None


def test_290_location_mimetype_absent_branch( ):
    ''' Location-based mimetype inference when mimetype is absent. '''
    content = b'test content'
    behaviors = detextive.Behaviors(
        mimetype_detect = True )
    result = _inference.infer_mimetype_charset_confidence(
        content,
        behaviors = behaviors,
        http_content_type = '',
        location = 'unknown_file_type' )
    assert result[0] is not None
    assert result[1] is not None


# HTTP Content-Type Tests (300-399): HTTP parsing functions and edge cases

def test_300_http_content_type_empty_mimetype( ):
    ''' HTTP Content-Type with empty mimetype returns absent values. '''
    mimetype, charset = _inference.parse_http_content_type( '' )
    assert _internals.is_absent( mimetype )
    assert _internals.is_absent( charset )
    mimetype, charset = _inference.parse_http_content_type( ';' )
    assert _internals.is_absent( mimetype )
    assert _internals.is_absent( charset )


def test_310_http_validation_charset_absent( ):
    ''' HTTP validation with textual mimetype but no charset parameter. '''
    content = b'test content'
    mimetype_result, charset_result = (
        _inference.infer_mimetype_charset_confidence(
            content,
            http_content_type = 'text/plain' ) )
    assert mimetype_result.mimetype == 'text/plain'
    assert charset_result is not None
    assert isinstance( charset_result.charset, str )


def test_320_mimetype_detection_disabled( ):
    ''' Disabled MIME detection still honors parsed HTTP metadata. '''
    content = b'test content'
    behaviors = detextive.Behaviors(
        mimetype_detect = False )
    result = _inference.infer_mimetype_charset_confidence(
        content,
        behaviors = behaviors,
        http_content_type = 'text/plain; charset=utf-8' )
    assert result[0].mimetype == 'text/plain'
    assert result[1] is not None


def test_330_http_content_type_no_charset_param( ):
    ''' HTTP Content-Type with textual type but no charset parameter. '''
    mimetype, charset = _inference.parse_http_content_type(
        'text/plain; boundary=something; encoding=base64' )
    assert mimetype == 'text/plain'
    assert _internals.is_absent( charset )


def test_332_http_content_type_malformed_charset_param( ):
    ''' Malformed charset parameter is treated as absent. '''
    mimetype, charset = _inference.parse_http_content_type(
        'text/plain; charset' )
    assert mimetype == 'text/plain'
    assert _internals.is_absent( charset )


def test_334_http_validation_malformed_charset_param( ):
    ''' Malformed charset parameter falls back to standard inference. '''
    content = b'test content'
    mimetype_result, charset_result = (
        _inference.infer_mimetype_charset_confidence(
            content,
            http_content_type = 'text/plain; charset' ) )
    assert mimetype_result.mimetype == 'text/plain'
    assert isinstance( charset_result.charset, str )


def test_340_http_validation_mimetype_present( ):
    ''' HTTP validation when mimetype is present (not absent). '''
    content = b'test content'
    mimetype_result, charset_result = (
        _inference.infer_mimetype_charset_confidence(
            content,
            http_content_type = 'application/json; charset=utf-8' ) )
    assert mimetype_result.mimetype == 'application/json'
    assert charset_result.charset == 'utf-8'


def test_350_http_validation_mimetype_not_absent( ):
    ''' HTTP validation when mimetype is not absent. '''
    content = b'{"test": "json"}'
    mimetype_result, charset_result = (
        _inference.infer_mimetype_charset_confidence(
            content,
            http_content_type = 'application/json; charset=utf-8' ) )
    assert mimetype_result.mimetype == 'application/json'
    assert mimetype_result.confidence == 0.9
    assert charset_result.charset == 'utf-8'
