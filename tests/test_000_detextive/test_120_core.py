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


''' Core types, enums, and behaviors. '''


import pytest

import detextive.core as _core
import detextive.exceptions as _exceptions


# Basic Tests (000-099): Module import verification, Constant value validation

def test_000_imports( ):
    ''' Core types and functions are accessible from core module. '''
    assert hasattr( _core, 'Behaviors' )
    assert hasattr( _core, 'BehaviorTristate' )
    assert hasattr( _core, 'CodecSpecifiers' )
    assert hasattr( _core, 'DetectFailureActions' )


def test_100_behaviors_detect_flags_require_boolean( ):
    ''' Detect flags reject non-boolean values at construction time. '''
    with pytest.raises( _exceptions.BehaviorsInvalidity ):
        _core.Behaviors( charset_detect = _core.BehaviorTristate.Never )
    with pytest.raises( _exceptions.BehaviorsInvalidity ):
        _core.Behaviors( mimetype_detect = _core.BehaviorTristate.Never )
    with pytest.raises( _exceptions.BehaviorsInvalidity ):
        _core.Behaviors( utf_16_32_requires_byte_order = 'yes' )


def test_110_behaviors_detect_flags_accept_boolean( ):
    ''' Detect flags accept explicit boolean values. '''
    behaviors = _core.Behaviors(
        charset_detect = False,
        mimetype_detect = True,
        utf_16_32_requires_byte_order = True )
    assert behaviors.charset_detect is False
    assert behaviors.mimetype_detect is True
    assert behaviors.utf_16_32_requires_byte_order is True
