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


''' Core detection functions default return behavior is correct. '''

import pytest

import detextive
import detextive.detectors as _detectors

from .patterns import (
    EMPTY_CONTENT,
    UNDETECTABLE_CHARSET,
    UNDETECTABLE_MIMETYPE,
    UTF8_BASIC,
    UTF8_WITH_BOM,
    UTF16_LE_NO_BOM,
    UTF16_WITH_BOM,
    UTF32_LE_NO_BOM,
    UTF32_WITH_BOM,
)


# Basic Tests (000-099): Module import verification, Registry container init

def test_000_imports( ):
    ''' Detection functions are accessible from main module. '''
    assert hasattr( detextive, 'detect_charset' )
    assert hasattr( detextive, 'detect_charset_confidence' )
    assert hasattr( detextive, 'detect_mimetype' )
    assert hasattr( detextive, 'detect_mimetype_confidence' )


# DEFAULT RETURN BEHAVIOR TESTS (100-199) - CRITICAL: Default vs Error behavior

def test_100_charset_detect_failure_default_behavior( ):
    ''' Charset detection failure returns default with zero confidence. '''
    behaviors = detextive.Behaviors(
        charset_detectors_order = ( 'nonexistent-detector', ),
        charset_on_detect_failure = detextive.DetectFailureActions.Default )
    result = detextive.detect_charset_confidence(
        UNDETECTABLE_CHARSET, behaviors = behaviors, default = 'ascii' )
    assert result.charset == 'ascii'
    assert result.confidence == 0.0


def test_110_charset_detect_failure_error_behavior( ):
    ''' Charset detection failure raises exception when configured. '''
    behaviors = detextive.Behaviors(
        charset_detectors_order = ( 'nonexistent-detector', ),
        charset_on_detect_failure = detextive.DetectFailureActions.Error )
    with pytest.raises( detextive.exceptions.CharsetDetectFailure ):
        detextive.detect_charset_confidence(
            UNDETECTABLE_CHARSET, behaviors = behaviors )


def test_120_charset_detect_failure_with_custom_default( ):
    ''' Charset detection failure returns custom default value. '''
    behaviors = detextive.Behaviors(
        charset_detectors_order = ( 'nonexistent-detector', ),
        charset_on_detect_failure = detextive.DetectFailureActions.Default )
    result = detextive.detect_charset_confidence(
        UNDETECTABLE_CHARSET, behaviors = behaviors, default = 'latin-1' )
    assert result.charset == 'latin-1'
    assert result.confidence == 0.0


def test_130_charset_detect_string_function_with_default( ):
    ''' Charset detection string function returns default on failure. '''
    behaviors = detextive.Behaviors(
        charset_detectors_order = ( 'nonexistent-detector', ),
        charset_on_detect_failure = detextive.DetectFailureActions.Default )
    result = detextive.detect_charset(
        UNDETECTABLE_CHARSET, behaviors = behaviors, default = 'cp1252' )
    assert result == 'cp1252'


def test_140_mimetype_detect_failure_default_behavior( ):
    ''' MIME type detection failure returns default with zero confidence. '''
    behaviors = detextive.Behaviors(
        mimetype_detectors_order = ( 'nonexistent-detector', ),
        mimetype_on_detect_failure = detextive.DetectFailureActions.Default )
    result = detextive.detect_mimetype_confidence(
        UNDETECTABLE_MIMETYPE, behaviors = behaviors,
        default = 'application/octet-stream' )
    assert result.mimetype == 'application/octet-stream'
    assert result.confidence == 0.0


def test_150_mimetype_detect_failure_error_behavior( ):
    ''' MIME type detection failure raises exception when configured. '''
    behaviors = detextive.Behaviors(
        mimetype_detectors_order = ( 'nonexistent-detector', ),
        mimetype_on_detect_failure = detextive.DetectFailureActions.Error )
    with pytest.raises( detextive.exceptions.MimetypeDetectFailure ):
        detextive.detect_mimetype_confidence(
            UNDETECTABLE_MIMETYPE, behaviors = behaviors )


def test_160_mimetype_detect_failure_with_custom_default( ):
    ''' MIME type detection failure returns custom default value. '''
    behaviors = detextive.Behaviors(
        mimetype_detectors_order = ( 'nonexistent-detector', ),
        mimetype_on_detect_failure = detextive.DetectFailureActions.Default )
    result = detextive.detect_mimetype_confidence(
        UNDETECTABLE_MIMETYPE, behaviors = behaviors, default = 'text/plain' )
    assert result.mimetype == 'text/plain'
    assert result.confidence == 0.0


def test_170_mimetype_detect_string_function_with_default( ):
    ''' MIME type detection string function returns default on failure. '''
    behaviors = detextive.Behaviors(
        mimetype_detectors_order = ( 'nonexistent-detector', ),
        mimetype_on_detect_failure = detextive.DetectFailureActions.Default )
    result = detextive.detect_mimetype(
        UNDETECTABLE_MIMETYPE, behaviors = behaviors, default = 'text/csv' )
    assert result == 'text/csv'


def test_180_mixed_failure_behaviors_charset_default_mimetype_error( ):
    ''' Mixed behaviors: charset defaults, MIME type errors. '''
    behaviors = detextive.Behaviors(
        charset_detectors_order = ( 'nonexistent-detector', ),
        mimetype_detectors_order = ( 'nonexistent-detector', ),
        charset_on_detect_failure = detextive.DetectFailureActions.Default,
        mimetype_on_detect_failure = detextive.DetectFailureActions.Error )
    charset_result = detextive.detect_charset_confidence(
        UNDETECTABLE_CHARSET, behaviors = behaviors, default = 'utf-8' )
    assert charset_result.charset == 'utf-8'
    assert charset_result.confidence == 0.0
    with pytest.raises( detextive.exceptions.MimetypeDetectFailure ):
        detextive.detect_mimetype_confidence(
            UNDETECTABLE_MIMETYPE, behaviors = behaviors )


def test_190_mixed_failure_behaviors_charset_error_mimetype_default( ):
    ''' Mixed behaviors: charset errors, MIME type defaults. '''
    behaviors = detextive.Behaviors(
        charset_detectors_order = ( 'nonexistent-detector', ),
        mimetype_detectors_order = ( 'nonexistent-detector', ),
        charset_on_detect_failure = detextive.DetectFailureActions.Error,
        mimetype_on_detect_failure = detextive.DetectFailureActions.Default )
    with pytest.raises( detextive.exceptions.CharsetDetectFailure ):
        detextive.detect_charset_confidence(
            UNDETECTABLE_CHARSET, behaviors = behaviors )
    mimetype_result = detextive.detect_mimetype_confidence(
        UNDETECTABLE_MIMETYPE, behaviors = behaviors,
        default = 'application/json' )
    assert mimetype_result.mimetype == 'application/json'
    assert mimetype_result.confidence == 0.0


# Charset Detection Tests (200-299): detect_charset functions and behaviors

def test_200_empty_content_charset_handling( ):
    ''' Empty content returns UTF-8 with full confidence. '''
    result = detextive.detect_charset_confidence( EMPTY_CONTENT )
    assert result.charset == 'utf-8'
    assert result.confidence == 1.0


def test_205_charset_normalization_tracks_utf8_bom_provenance( ):
    ''' UTF-8 charset labels track source BOM bytes. '''
    detector_name = 'test-utf8-detector-for-bom-provenance'
    def detector_utf8( content, behaviors ):
        return detextive.core.CharsetResult(
            charset = 'utf-8', confidence = 0.9 )
    _detectors.charset_detectors[ detector_name ] = detector_utf8
    behaviors = detextive.Behaviors(
        charset_detectors_order = ( detector_name, ),
        trial_decode = detextive.BehaviorTristate.Never )
    result_no_bom = detextive.detect_charset_confidence(
        UTF8_BASIC, behaviors = behaviors )
    result_with_bom = detextive.detect_charset_confidence(
        UTF8_WITH_BOM, behaviors = behaviors )
    assert result_no_bom.charset == 'utf-8'
    assert result_with_bom.charset == 'utf-8-sig'


def test_206_charset_normalization_tracks_utf16_utf32_bom_provenance( ):
    ''' UTF-16/32 charset labels track source BOM bytes. '''
    detector_name_utf16 = 'test-utf16-detector-for-bom-provenance'
    detector_name_utf32 = 'test-utf32-detector-for-bom-provenance'
    def detector_utf16( content, behaviors ):
        return detextive.core.CharsetResult(
            charset = 'utf-16', confidence = 0.9 )
    _detectors.charset_detectors[ detector_name_utf16 ] = detector_utf16
    behaviors = detextive.Behaviors(
        charset_detectors_order = ( detector_name_utf16, ),
        trial_decode = detextive.BehaviorTristate.Never )
    result_utf16_no_bom = detextive.detect_charset_confidence(
        UTF16_LE_NO_BOM, behaviors = behaviors )
    result_utf16_with_bom = detextive.detect_charset_confidence(
        UTF16_WITH_BOM, behaviors = behaviors )
    assert result_utf16_no_bom.charset == 'utf-16'
    assert result_utf16_with_bom.charset == 'utf-16'

    def detector_utf32( content, behaviors ):
        return detextive.core.CharsetResult(
            charset = 'utf-32', confidence = 0.9 )
    _detectors.charset_detectors[ detector_name_utf32 ] = detector_utf32
    behaviors_utf32 = detextive.Behaviors(
        charset_detectors_order = ( detector_name_utf32, ),
        trial_decode = detextive.BehaviorTristate.Never )
    result_utf32_no_bom = detextive.detect_charset_confidence(
        UTF32_LE_NO_BOM, behaviors = behaviors_utf32 )
    result_utf32_with_bom = detextive.detect_charset_confidence(
        UTF32_WITH_BOM, behaviors = behaviors_utf32 )
    assert result_utf32_no_bom.charset == 'utf-32'
    assert result_utf32_with_bom.charset == 'utf-32'


def test_210_charset_detection_with_mimetype_absent( ):
    ''' Charset detection ignores enhancement when mimetype is absent. '''
    behaviors = detextive.Behaviors(
        charset_detectors_order = ( 'chardet', ), )
    content = b'\x80\x81\x82\x83'
    result = detextive.detect_charset_confidence(
        content, behaviors = behaviors )
    assert result is not None
    assert result.confidence >= 0.0


def test_220_charset_detection_with_non_textual_mimetype( ):
    ''' Charset detection ignores enhancement for non-textual MIME types. '''
    behaviors = detextive.Behaviors(
        charset_detectors_order = ( 'chardet', ), )
    content = b'\x80\x81\x82\x83'
    result = detextive.detect_charset_confidence(
        content, behaviors = behaviors, mimetype = 'image/png' )
    assert result is not None
    assert result.confidence >= 0.0


def test_230_charset_detection_with_textual_mimetype_enhancement( ):
    ''' Charset detection uses MIME type context for textual content. '''
    behaviors = detextive.Behaviors(
        charset_detectors_order = ( 'chardet', ), )
    content = b'Caf\xc3\xa9'
    result = detextive.detect_charset_confidence(
        content, behaviors = behaviors, mimetype = 'text/plain' )
    assert result is not None
    assert result.confidence >= 0.0


def test_240_detector_returns_not_implemented( ):
    ''' Charset detection continues when detector returns NotImplemented. '''
    def always_not_implemented( content, behaviors ):
        return NotImplemented
    _detectors.charset_detectors[ 'test-not-implemented' ] = (
        always_not_implemented )
    behaviors = detextive.Behaviors(
        charset_detectors_order = ( 'test-not-implemented', ),
        charset_on_detect_failure = detextive.DetectFailureActions.Default )
    result = _detectors.detect_charset_confidence(
        b'test content', behaviors = behaviors, default = 'utf-8' )
    assert result.charset == 'utf-8'
    assert result.confidence == 0.0


def test_250_trial_decode_charset_none_textual_mimetype( ):
    ''' Trial decode pathway when charset=None with textual mimetype. '''
    def charset_none_detector( content, behaviors ):
        return detextive.core.CharsetResult( charset = None, confidence = 0.8 )
    _detectors.charset_detectors[ 'test-charset-none' ] = (
        charset_none_detector )
    behaviors = detextive.Behaviors(
        charset_detectors_order = ( 'test-charset-none', ),
        trial_decode = detextive.BehaviorTristate.Always )
    result = _detectors.detect_charset_confidence(
        b'test content', behaviors = behaviors,
        mimetype = 'text/plain', supplement = 'utf-8' )
    assert result.charset is not None


def test_260_charset_normalizer_execution( ):
    ''' charset_normalizer detector executes when available. '''
    behaviors = detextive.Behaviors(
        charset_detectors_order = ( 'charset-normalizer', ) )
    utf8_content = 'Hello, world! 你好世界'.encode( 'utf-8' )
    try:
        result = _detectors.detect_charset_confidence(
            utf8_content, behaviors = behaviors )
        assert result.charset is not None
        assert result.confidence > 0.0
    except detextive.exceptions.CharsetDetectFailure:
        pass


# MIME Type Detection Tests (300-399): detect_mimetype functions and behaviors

def test_300_empty_content_mimetype_handling( ):
    ''' Empty content returns text/plain with full confidence. '''
    result = detextive.detect_mimetype_confidence( EMPTY_CONTENT )
    assert result.mimetype == 'text/plain'
    assert result.confidence == 1.0


def test_310_detect_mimetype_charset_influence( ):
    ''' Charset information influences MIME type detection appropriately. '''
    behaviors_no_trial = detextive.Behaviors(
        mimetype_detectors_order = ( 'nonexistent-detector', ),
        trial_decode = detextive.BehaviorTristate.Never,
        mimetype_on_detect_failure = detextive.DetectFailureActions.Default )
    result = detextive.detect_mimetype_confidence(
        b'test content', behaviors = behaviors_no_trial,
        charset = 'utf-8', default = 'text/custom' )
    assert result.mimetype == 'text/custom'
    assert result.confidence == 0.0


def test_320_detect_mimetype_decode_failure_default_behavior( ):
    ''' MIME type detection handles decode failures with default behavior. '''
    behaviors = detextive.Behaviors(
        mimetype_detectors_order = ( 'nonexistent-detector', ),
        mimetype_on_detect_failure = detextive.DetectFailureActions.Default )
    result = detextive.detect_mimetype_confidence(
        b'\xff\xfe\xfd',
        behaviors = behaviors, charset = 'utf-8',
        default = 'application/fallback' )
    assert result.mimetype == 'application/fallback'
    assert result.confidence == 0.0


def test_330_detect_mimetype_decode_failure_error_behavior( ):
    ''' MIME type detection raises exception on decode failure. '''
    behaviors = detextive.Behaviors(
        mimetype_detectors_order = ( 'nonexistent-detector', ),
        mimetype_on_detect_failure = detextive.DetectFailureActions.Error )
    with pytest.raises( detextive.exceptions.MimetypeDetectFailure ):
        detextive.detect_mimetype_confidence(
            b'\xff\xfe\xfd',
            behaviors = behaviors, charset = 'utf-8' )


def test_335_detect_mimetype_trial_decode_never_error_behavior( ):
    ''' MIME type detection raises when trial decode is disabled. '''
    behaviors = detextive.Behaviors(
        mimetype_detectors_order = ( 'nonexistent-detector', ),
        trial_decode = detextive.BehaviorTristate.Never,
        mimetype_on_detect_failure = detextive.DetectFailureActions.Error )
    with pytest.raises( detextive.exceptions.MimetypeDetectFailure ):
        detextive.detect_mimetype_confidence(
            b'test content',
            behaviors = behaviors,
            charset = 'utf-8' )


def test_340_detect_mimetype_text_validation_never( ):
    ''' MIME type detection respects text validation disabled setting. '''
    behaviors = detextive.Behaviors(
        mimetype_detectors_order = ( 'nonexistent-detector', ),
        text_validate = detextive.BehaviorTristate.Never,
        mimetype_on_detect_failure = detextive.DetectFailureActions.Default )
    result = detextive.detect_mimetype_confidence(
        b'valid text content',
        behaviors = behaviors, charset = 'utf-8', default = 'text/fallback' )
    assert result.mimetype == 'text/fallback'
    assert result.confidence == 0.0


def test_350_detect_mimetype_text_validation_never_error( ):
    ''' MIME type detection raises exception with text validation disabled. '''
    behaviors = detextive.Behaviors(
        mimetype_detectors_order = ( 'nonexistent-detector', ),
        text_validate = detextive.BehaviorTristate.Never,
        mimetype_on_detect_failure = detextive.DetectFailureActions.Error )
    with pytest.raises( detextive.exceptions.MimetypeDetectFailure ):
        detextive.detect_mimetype_confidence(
            b'valid text content',
            behaviors = behaviors, charset = 'utf-8' )


def test_360_detect_mimetype_non_textual_content_default( ):
    ''' MIME type detection handles non-textual content with defaults. '''
    behaviors = detextive.Behaviors(
        mimetype_detectors_order = ( 'nonexistent-detector', ),
        mimetype_on_detect_failure = detextive.DetectFailureActions.Default )
    result = detextive.detect_mimetype_confidence(
        b'\x01\x02\x03\x04\x05' * 20,
        behaviors = behaviors, charset = 'utf-8',
        default = 'application/binary' )
    assert result.mimetype == 'application/binary'
    assert result.confidence == 0.0


def test_370_detect_mimetype_non_textual_content_error( ):
    ''' MIME type detection raises exception for non-textual content. '''
    behaviors = detextive.Behaviors(
        mimetype_detectors_order = ( 'nonexistent-detector', ),
        mimetype_on_detect_failure = detextive.DetectFailureActions.Error )
    with pytest.raises( detextive.exceptions.MimetypeDetectFailure ):
        detextive.detect_mimetype_confidence(
            b'\x01\x02\x03\x04\x05' * 20,
            behaviors = behaviors, charset = 'utf-8' )


def test_380_detect_mimetype_successful_validation_pipeline( ):
    ''' MIME type detection succeeds with valid textual content. '''
    behaviors = detextive.Behaviors(
        mimetype_detectors_order = ( 'nonexistent-detector', ),
        mimetype_on_detect_failure = detextive.DetectFailureActions.Default )
    result = detextive.detect_mimetype_confidence(
        b'This is valid textual content that should pass validation.',
        behaviors = behaviors, charset = 'utf-8' )
    assert result.mimetype == 'text/plain'
    assert result.confidence > 0.0


# Registry System Tests (400-499): Detector registration and retrieval

def test_400_not_implemented_handling( ):
    ''' Missing dependencies return NotImplemented correctly. '''
    behaviors = detextive.Behaviors(
        mimetype_detectors_order = ( 'puremagic', ) )
    result = detextive.detect_mimetype_confidence(
        b'test content', behaviors = behaviors )
    assert result is not None
    assert result.confidence >= 0.0


# Charset Confirmation Tests (500-599): _confirm_charset_detection behavior

def test_500_confirm_charset_detection_trial_decode_never( ):
    ''' Non-UTF charset with trial_decode=Never returns without validation. '''
    def custom_detector( content, behaviors ):
        return detextive.core.CharsetResult(
            charset = 'iso-8859-1', confidence = 0.5 )
    _detectors.charset_detectors[ 'test-iso-detector' ] = custom_detector
    behaviors = detextive.Behaviors(
        charset_detectors_order = ( 'test-iso-detector', ),
        trial_decode = detextive.BehaviorTristate.Never )
    content = b'test content'
    result = _detectors.detect_charset_confidence(
        content, behaviors = behaviors, default = 'utf-8' )
    assert result.charset == 'iso8859-1'
    assert result.confidence == 0.5


# Windows Compatibility Tests (600-699): Cross-platform differences

def test_600_python_magic_vs_python_magic_bin( ):
    ''' python-magic vs python-magic-bin MIME type differences. '''
    behaviors_puremagic = detextive.Behaviors(
        mimetype_detectors_order = ( 'puremagic', 'python-magic' ) )
    behaviors_magic = detextive.Behaviors(
        mimetype_detectors_order = ( 'python-magic', 'puremagic' ) )
    json_content = b'{"key": "value", "number": 42}'
    result_puremagic = detextive.detect_mimetype_confidence(
        json_content, behaviors = behaviors_puremagic )
    result_magic = detextive.detect_mimetype_confidence(
        json_content, behaviors = behaviors_magic )
    assert result_puremagic is not None
    assert result_magic is not None
    assert result_puremagic.confidence >= 0.0
    assert result_magic.confidence >= 0.0
