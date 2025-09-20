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
import detextive.charsets as _charsets

from . import patterns as _patterns


#============================================================================#
# Basic Tests (000-099): Module import verification
#============================================================================#

def test_000_imports( ):
    ''' Charset functions are accessible from main module. '''
    assert hasattr( detextive, 'charsets' )


#============================================================================#
# OS Charset Detection Tests (100-199): discover_os_charset_default function
#============================================================================#

def test_100_discover_os_charset_default( ):
    ''' OS charset detection returns valid charset name. '''
    charset = _charsets.discover_os_charset_default( )
    assert isinstance( charset, str )
    assert len( charset ) > 0


def test_110_attempt_decodes_os_default_codec( ):
    ''' Attempt decodes uses OS default codec when specified. '''
    behaviors = detextive.Behaviors(
        trial_codecs = ( detextive.CodecSpecifiers.OsDefault, ) )
    text, result = _charsets.attempt_decodes(
        _patterns.UTF8_BASIC, behaviors = behaviors )
    assert isinstance( text, str )
    assert result.charset is not None


def test_120_attempt_decodes_python_default_codec( ):
    ''' Attempt decodes uses Python default codec when specified. '''
    behaviors = detextive.Behaviors(
        trial_codecs = ( detextive.CodecSpecifiers.PythonDefault, ) )
    text, result = _charsets.attempt_decodes(
        _patterns.UTF8_BASIC, behaviors = behaviors )
    assert isinstance( text, str )
    assert result.charset is not None


#============================================================================#
# Codec Resolution Tests (200-299): CodecSpecifiers enum handling
#============================================================================#

def test_200_codec_specifiers_os_default( ):
    ''' OsDefault codec specifier behavior in attempt_decodes. '''
    behaviors = detextive.Behaviors(
        trial_codecs = ( detextive.CodecSpecifiers.OsDefault, ) )
    text, result = _charsets.attempt_decodes(
        _patterns.UTF8_BASIC, behaviors = behaviors )
    assert isinstance( text, str )
    assert result.charset is not None


def test_210_codec_specifiers_python_default( ):
    ''' PythonDefault codec specifier behavior in attempt_decodes. '''
    behaviors = detextive.Behaviors(
        trial_codecs = ( detextive.CodecSpecifiers.PythonDefault, ) )
    text, result = _charsets.attempt_decodes(
        _patterns.UTF8_BASIC, behaviors = behaviors )
    assert isinstance( text, str )
    assert result.charset is not None


def test_220_codec_specifiers_user_supplement( ):
    ''' UserSupplement codec specifier behavior with supplement parameter. '''
    behaviors = detextive.Behaviors(
        trial_codecs = ( detextive.CodecSpecifiers.UserSupplement, ) )
    text, result = _charsets.attempt_decodes(
        _patterns.UTF8_BASIC, behaviors = behaviors, supplement = 'utf-8' )
    assert text == 'Hello, world!'
    assert result.charset == 'utf-8'


def test_230_codec_specifiers_string_codec( ):
    ''' String codec names are handled directly in attempt_decodes. '''
    behaviors = detextive.Behaviors( trial_codecs = ( 'ascii', ) )
    text, result = _charsets.attempt_decodes(
        _patterns.UTF8_BASIC, behaviors = behaviors )
    assert text == 'Hello, world!'
    assert result.charset == 'ascii'


def test_240_invalid_codec_type_handling( ):
    ''' Invalid codec types are skipped correctly. '''
    behaviors = detextive.Behaviors(
        trial_codecs = ( 42, 'utf-8' ),  # 42 is not str | CodecSpecifiers
    )
    content = b'test content'
    text, result = _charsets.attempt_decodes(
        content, behaviors = behaviors )
    assert text == 'test content'
    assert result.charset == 'utf-8'


#============================================================================#
# Trial Decode Tests (300-399): attempt_decodes and trial_decode_as_confident
#============================================================================#

def test_300_trial_decode_failure_without_inference( ):
    ''' Trial decode raises failure when inference is absent. '''
    content = b'Hello, world!'
    behaviors = detextive.Behaviors(
        trial_decode = detextive.BehaviorTristate.Never )
    with pytest.raises( detextive.exceptions.CharsetDetectFailure ):
        _charsets.trial_decode_as_confident(
            content, behaviors = behaviors, confidence = 0.5 )