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


''' Public interfaces. '''


from . import __


class BehaviorTristate( __.enum.Enum ):
    ''' When to apply behavior. '''

    Never       = __.enum.auto( )
    AsNeeded    = __.enum.auto( )
    Always      = __.enum.auto( )


class CodecSpecifiers( __.enum.Enum ):
    ''' Specifiers for dynamic codecs. '''

    FromInference   = __.enum.auto( )
    OsDefault       = __.enum.auto( )
    PythonDefault   = __.enum.auto( )
    UserDefault     = __.enum.auto( )


class Behaviors( __.immut.DataclassObject ):
    ''' How functions behave. '''

    charset_detect: __.typx.Annotated[
        BehaviorTristate,
        __.ddoc.Doc( ''' When to detect charset from content. ''' ),
    ] = BehaviorTristate.AsNeeded
    charset_on_decode_error: __.typx.Annotated[
        str,
        __.ddoc.Doc(
            ''' Response to charset decoding errors.

                Standard values are 'ignore', 'replace', and 'strict'.
                Can also be any other name which has been registered via
                the 'register_error' function in the Python standard library
                'codecs' module.
            ''' ),
    ] = 'strict'
    charset_promotions: __.typx.Annotated[
        __.cabc.Mapping[ str, str ],
        __.ddoc.Doc(
            ''' Which detected charsets to promote to other charsets.

                E.g., 7-bit ASCII to UTF-8.
            ''' ),
    ] = __.immut.Dictionary( ( ( 'ascii', 'utf-8' ), ) )
    charset_trial_codecs: __.typx.Annotated[
        __.cabc.Sequence[ str | CodecSpecifiers ],
        __.ddoc.Doc( ''' Sequence of codec names or specifiers. ''' ),
    ] = ( CodecSpecifiers.FromInference, CodecSpecifiers.UserDefault )
    charset_trial_decode: __.typx.Annotated[
        BehaviorTristate,
        __.ddoc.Doc(
            ''' When to perform trial decode of content with charset. ''' ),
    ] = BehaviorTristate.AsNeeded
    mimetype_detect: __.typx.Annotated[
        BehaviorTristate,
        __.ddoc.Doc( ''' When to detect MIME type from content. ''' ),
    ] = BehaviorTristate.AsNeeded
    text_validate: __.typx.Annotated[
        BehaviorTristate,
        __.ddoc.Doc( ''' When to validate text. ''' ),
    ] = BehaviorTristate.AsNeeded


BEHAVIORS_DEFAULT = Behaviors( )
