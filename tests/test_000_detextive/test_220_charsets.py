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


''' Charset codec edge cases and fallback mechanisms. '''


import pytest

import detextive

from .patterns import (
    UTF8_BASIC,
)


def test_000_imports( ):
    ''' Charset functions are accessible from main module. '''
    assert hasattr( detextive, 'charsets' )


def test_100_attempt_decodes_os_default_codec( ):
    ''' Attempt decodes uses OS default codec when specified. '''
    behaviors = detextive.Behaviors(
        trial_codecs = ( detextive.CodecSpecifiers.OsDefault, ) )
    text, result = detextive.charsets.attempt_decodes(
        UTF8_BASIC, behaviors = behaviors )
    assert isinstance( text, str )
    assert result.charset is not None


def test_110_attempt_decodes_python_default_codec( ):
    ''' Attempt decodes uses Python default codec when specified. '''
    behaviors = detextive.Behaviors(
        trial_codecs = ( detextive.CodecSpecifiers.PythonDefault, ) )
    text, result = detextive.charsets.attempt_decodes(
        UTF8_BASIC, behaviors = behaviors )
    assert isinstance( text, str )
    assert result.charset is not None


def test_120_attempt_decodes_user_supplement_codec( ):
    ''' Attempt decodes uses user supplement codec when provided. '''
    behaviors = detextive.Behaviors(
        trial_codecs = ( detextive.CodecSpecifiers.UserSupplement, ) )
    text, result = detextive.charsets.attempt_decodes(
        UTF8_BASIC, behaviors = behaviors, supplement = 'utf-8' )
    assert text == 'Hello, world!'
    assert result.charset == 'utf-8'


def test_130_attempt_decodes_string_codec( ):
    ''' Attempt decodes uses explicit string codec. '''
    behaviors = detextive.Behaviors( trial_codecs = ( 'ascii', ) )
    text, result = detextive.charsets.attempt_decodes(
        UTF8_BASIC, behaviors = behaviors )
    assert text == 'Hello, world!'
    assert result.charset == 'ascii'


def test_200_trial_decode_failure_without_inference( ):
    ''' Trial decode raises failure when inference is absent. '''
    content = b'Hello, world!'
    behaviors = detextive.Behaviors(
        trial_decode = detextive.BehaviorTristate.Never )
    with pytest.raises( detextive.exceptions.CharsetDetectFailure ):
        detextive.charsets.trial_decode_as_confident(
            content, behaviors = behaviors, confidence = 0.5 )