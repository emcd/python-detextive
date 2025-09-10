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


''' Exception classes functionality is correct. '''


import pytest

from .__ import PACKAGE_NAME, cache_import_module


@pytest.fixture
def exceptions_module( ):
    ''' Provides access to exceptions module. '''
    return cache_import_module( f"{PACKAGE_NAME}.exceptions" )


def test_100_exception_hierarchy( exceptions_module ):
    ''' Exception hierarchy follows expected inheritance pattern. '''
    assert issubclass(
        exceptions_module.Omnierror, exceptions_module.Omniexception )
    assert issubclass( exceptions_module.Omniexception, BaseException )
    assert issubclass( exceptions_module.Omnierror, Exception )


# def test_200_exception_catching_via_base_classes( exceptions_module ):
#     ''' Package exceptions are catchable via base exception classes. '''
#     exceptions = [
#         exceptions_module.CharsetDetectFailure( 'test' ),
#         exceptions_module.ContentDecodeFailure( 'test', 'utf-8' ),
#         exceptions_module.TextualMimetypeInvalidity( 'test', 'image/jpeg' ),
#     ]
#     for exc in exceptions:
#         assert isinstance( exc, exceptions_module.Omnierror )
#         assert isinstance( exc, exceptions_module.Omniexception )
