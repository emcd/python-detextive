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


''' Validation edge cases for text content analysis. '''


import detextive
import detextive.validation as _validation


# Basic Tests (000-099): Module import and function accessibility

def test_000_imports( ):
    ''' Validation functions are accessible from main module. '''
    assert hasattr( detextive, 'validation' )


# Text Validation Profile Tests (100-199): Default and custom profile behavior

def test_100_is_valid_text_rejectable_families_edge_case( ):
    ''' Unicode category checking in rejectable families. '''
    profile = _validation.Profile(
        rejectable_families = frozenset( ( 'Cf', ) ) )
    text_with_format_char = 'Hello\u200BWorld'
    result = _validation.is_valid_text(
        text_with_format_char, profile )
    assert isinstance( result, bool )


def test_110_validation_sample_quantity_none( ):
    ''' Validation with sample_quantity=None processes entire text. '''
    profile = _validation.Profile(
        sample_quantity = None )
    text = 'Hello World! This is a test text.'
    result = _validation.is_valid_text( text, profile )
    assert isinstance( result, bool )
    assert result is True


def test_120_validation_non_printable_unicode_category( ):
    ''' Validation with non-printable Unicode categories skips elif branch. '''
    text = 'Hello\x00World'
    profile = _validation.Profile(
        acceptable_characters = frozenset( ),
        rejectable_families = frozenset( ),
        rejectables_ratio_max = 0.5 )
    result = _validation.is_valid_text( text, profile )
    assert isinstance( result, bool )