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

from .patterns import (
    EMPTY_CONTENT,
    UNDETECTABLE_CHARSET,
    UNDETECTABLE_MIMETYPE,
)


def test_000_imports( ):
    ''' Detection functions are accessible from main module. '''
    assert hasattr( detextive, 'detect_charset' )
    assert hasattr( detextive, 'detect_charset_confidence' )
    assert hasattr( detextive, 'detect_mimetype' )
    assert hasattr( detextive, 'detect_mimetype_confidence' )


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


def test_200_mimetype_detect_failure_default_behavior( ):
    ''' MIME type detection failure returns default with zero confidence. '''
    behaviors = detextive.Behaviors(
        mimetype_detectors_order = ( 'nonexistent-detector', ),
        mimetype_on_detect_failure = detextive.DetectFailureActions.Default )
    result = detextive.detect_mimetype_confidence(
        UNDETECTABLE_MIMETYPE, behaviors = behaviors,
        default = 'application/octet-stream' )
    assert result.mimetype == 'application/octet-stream'
    assert result.confidence == 0.0


def test_210_mimetype_detect_failure_error_behavior( ):
    ''' MIME type detection failure raises exception when configured. '''
    behaviors = detextive.Behaviors(
        mimetype_detectors_order = ( 'nonexistent-detector', ),
        mimetype_on_detect_failure = detextive.DetectFailureActions.Error )
    with pytest.raises( detextive.exceptions.MimetypeDetectFailure ):
        detextive.detect_mimetype_confidence(
            UNDETECTABLE_MIMETYPE, behaviors = behaviors )


def test_220_mimetype_detect_failure_with_custom_default( ):
    ''' MIME type detection failure returns custom default value. '''
    behaviors = detextive.Behaviors(
        mimetype_detectors_order = ( 'nonexistent-detector', ),
        mimetype_on_detect_failure = detextive.DetectFailureActions.Default )
    result = detextive.detect_mimetype_confidence(
        UNDETECTABLE_MIMETYPE, behaviors = behaviors, default = 'text/plain' )
    assert result.mimetype == 'text/plain'
    assert result.confidence == 0.0


def test_230_mimetype_detect_string_function_with_default( ):
    ''' MIME type detection string function returns default on failure. '''
    behaviors = detextive.Behaviors(
        mimetype_detectors_order = ( 'nonexistent-detector', ),
        mimetype_on_detect_failure = detextive.DetectFailureActions.Default )
    result = detextive.detect_mimetype(
        UNDETECTABLE_MIMETYPE, behaviors = behaviors, default = 'text/csv' )
    assert result == 'text/csv'


def test_300_mixed_failure_behaviors_charset_default_mimetype_error( ):
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


def test_310_mixed_failure_behaviors_charset_error_mimetype_default( ):
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


def test_400_empty_content_charset_handling( ):
    ''' Empty content returns UTF-8 with full confidence. '''
    result = detextive.detect_charset_confidence( EMPTY_CONTENT )
    assert result.charset == 'utf-8'
    assert result.confidence == 1.0


def test_410_empty_content_mimetype_handling( ):
    ''' Empty content returns text/plain with full confidence. '''
    result = detextive.detect_mimetype_confidence( EMPTY_CONTENT )
    assert result.mimetype == 'text/plain'
    assert result.confidence == 1.0