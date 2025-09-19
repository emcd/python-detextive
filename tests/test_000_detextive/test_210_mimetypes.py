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


''' MIME type detection edge cases. '''


import detextive


def test_000_imports( ):
    ''' MIME type functions are accessible from main module. '''
    assert hasattr( detextive, 'mimetypes' )


def test_100_mimetype_from_location_unknown_extension( ):
    ''' Unknown file extension returns absent mimetype. '''
    result = detextive.mimetypes.mimetype_from_location( 'file.unknownext' )
    assert detextive.__.is_absent( result )


# def test_110_is_textual_mimetype_text_prefixes( ):
#     ''' Text prefix MIME types are identified as textual. '''
#     pass


# def test_120_is_textual_mimetype_application_json( ):
#     ''' Known textual application types are identified correctly. '''
#     pass


# def test_130_is_textual_mimetype_textual_suffixes( ):
#     ''' Textual suffix MIME types are identified correctly. '''
#     pass


# def test_140_is_textual_mimetype_non_textual_rejection( ):
#     ''' Non-textual MIME types are rejected correctly. '''
#     pass


# def test_150_is_textual_mimetype_empty_malformed( ):
#     ''' Empty and malformed MIME types are handled correctly. '''
#     pass


# def test_160_is_textual_mimetype_case_sensitivity( ):
#     ''' Case sensitivity in MIME type evaluation works correctly. '''
#     pass


# def test_200_mimetype_with_parameters( ):
#     ''' MIME types with parameters are handled correctly. '''
#     pass


# def test_210_vendor_specific_mimetypes( ):
#     ''' Vendor-specific MIME types are processed correctly. '''
#     pass


# def test_220_custom_unknown_mimetypes( ):
#     ''' Custom and unknown MIME types are handled appropriately. '''
#     pass


# def test_230_very_long_mimetype_strings( ):
#     ''' Very long MIME type strings are processed correctly. '''
#     pass


# def test_240_mimetypes_unusual_characters( ):
#     ''' MIME types with unusual characters are handled correctly. '''
#     pass