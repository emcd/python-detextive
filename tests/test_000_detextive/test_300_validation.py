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


def test_000_imports( ):
    ''' Validation functions are accessible from main module. '''
    assert hasattr( detextive, 'validation' )


def test_100_is_valid_text_rejectable_families_edge_case( ):
    ''' Unicode category checking in rejectable families. '''
    profile = detextive.validation.Profile(
        rejectable_families = frozenset( ( 'Cf', ) ) )
    text_with_format_char = 'Hello\u200BWorld'
    result = detextive.validation.is_valid_text(
        text_with_format_char, profile )
    assert isinstance( result, bool )