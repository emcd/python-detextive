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


import detextive.core as _core


# Basic Tests (000-099): Module import verification, Constant value validation

def test_000_imports( ):
    ''' Core types and functions are accessible from core module. '''
    assert hasattr( _core, 'Behaviors' )
    assert hasattr( _core, 'BehaviorTristate' )
    assert hasattr( _core, 'CodecSpecifiers' )
    assert hasattr( _core, 'DetectFailureActions' )