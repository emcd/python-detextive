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

from .patterns import (
    EMPTY_CONTENT,
)


# Basic Tests (000-099): Module import and function accessibility

def test_000_imports( ):
    ''' Decode function is accessible from main module. '''
    assert hasattr( detextive, 'decode' )


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
