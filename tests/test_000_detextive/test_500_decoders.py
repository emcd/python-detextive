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


import detextive

from .patterns import (
    EMPTY_CONTENT,
)


def test_000_imports( ):
    ''' Decode function is accessible from main module. '''
    assert hasattr( detextive, 'decode' )


def test_100_decode_inference_failure_fallback_to_utf8_sig( ):
    ''' Inference failure falls back to utf-8-sig with confidence. '''
    # Force inference failure by using empty detector orders
    behaviors = detextive.Behaviors(
        charset_detectors_order = ( 'nonexistent-detector', ),
        mimetype_detectors_order = ( 'nonexistent-detector', ),
        charset_on_detect_failure = detextive.DetectFailureActions.Error,
        mimetype_on_detect_failure = detextive.DetectFailureActions.Error )
    utf8_content = b'Hello, world!'
    result = detextive.decode(
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
    result = detextive.decode(
        content, behaviors = behaviors, charset_supplement = 'ascii' )
    assert result == 'Hello, world!'


def test_200_decode_empty_content_returns_empty_string( ):
    ''' Empty content decoding returns empty string immediately. '''
    result = detextive.decode( EMPTY_CONTENT )
    assert result == ''