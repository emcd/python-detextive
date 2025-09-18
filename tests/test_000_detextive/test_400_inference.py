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

from .patterns import (
    EMPTY_CONTENT,
    UTF8_BASIC,
)


def test_000_imports( ):
    ''' Inference functions are accessible from main module. '''
    assert hasattr( detextive, 'inference' )


def test_100_infer_charset_string_function( ):
    ''' Infer charset returns string instead of result object. '''
    charset = detextive.inference.infer_charset( UTF8_BASIC )
    assert isinstance( charset, str )
    assert charset is not None


def test_110_infer_charset_confidence_empty_content( ):
    ''' Empty content inference returns UTF-8 with full confidence. '''
    result = detextive.inference.infer_charset_confidence( EMPTY_CONTENT )
    assert result.charset == 'utf-8'
    assert result.confidence == 1.0


def test_120_infer_charset_confidence_http_content_type_parsing( ):
    ''' HTTP content type parsing extracts charset from header. '''
    content = UTF8_BASIC
    http_content_type = 'text/plain; charset=iso-8859-1'
    result = detextive.inference.infer_charset_confidence(
        content, http_content_type = http_content_type )
    assert result.charset == 'iso-8859-1'


def test_130_infer_charset_confidence_detection_fallback( ):
    ''' Falls back to detection when no other methods work. '''
    behaviors = detextive.Behaviors(
        charset_detect = detextive.BehaviorTristate.Always )
    result = detextive.inference.infer_charset_confidence(
        UTF8_BASIC, behaviors = behaviors )
    assert result.charset is not None
    assert result.confidence >= 0.0


def test_140_infer_charset_confidence_failure_when_no_detection( ):
    ''' Raises CharsetInferFailure when no detection methods available. '''
    behaviors = detextive.Behaviors(
        charset_detect = detextive.BehaviorTristate.Never,
        charset_detectors_order = ( 'nonexistent-detector', ),
        charset_on_detect_failure = detextive.DetectFailureActions.Error )
    with pytest.raises( detextive.exceptions.CharsetInferFailure ):
        detextive.inference.infer_charset_confidence(
            UTF8_BASIC, behaviors = behaviors )