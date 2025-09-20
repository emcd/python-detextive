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


''' Core types and behaviors. '''


from . import __
from . import nomina as _nomina


_STANDARD_CHARSET_PROMOTIONS = (
    ( 'ascii', 'utf-8-sig' ),
    ( 'utf-8', 'utf-8-sig' ),
)


CHARSET_DEFAULT = 'utf-8'
MIMETYPE_DEFAULT = 'application/octet-stream'


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
    UserSupplement  = __.enum.auto( )


class DetectFailureActions( __.enum.Enum ):
    ''' Possible responses to detection failure. '''

    Default     = __.enum.auto( )
    Error       = __.enum.auto( )


class Behaviors( __.immut.DataclassObject ):
    ''' How functions behave. '''

    bytes_quantity_confidence_divisor: __.typx.Annotated[
        int,
        __.ddoc.Doc(
            ''' Minimum number of bytes for full detection confidence. ''' ),
    ] = 1024
    charset_detect: __.typx.Annotated[
        BehaviorTristate,
        __.ddoc.Doc( ''' When to detect charset from content. ''' ),
    ] = BehaviorTristate.AsNeeded
    charset_detectors_order: __.typx.Annotated[
        __.cabc.Sequence[ str ],
        __.ddoc.Doc(
            ''' Order in which charset detectors should be applied. ''' ),
    ] = ( 'chardet', 'charset-normalizer' )
    charset_on_detect_failure: __.typx.Annotated[
        DetectFailureActions,
        __.ddoc.Doc( ''' Action to take on charset detection failure. ''' ),
    ] = DetectFailureActions.Default
    charset_promotions: __.typx.Annotated[
        __.cabc.Mapping[ str, str ],
        __.ddoc.Doc(
            ''' Which detected charsets to promote to other charsets.

                E.g., 7-bit ASCII to UTF-8.
            ''' ),
    ] = __.dcls.field(
        default_factory = (
            lambda: __.immut.Dictionary( _STANDARD_CHARSET_PROMOTIONS ) ) )
    mimetype_detect: __.typx.Annotated[
        BehaviorTristate,
        __.ddoc.Doc( ''' When to detect MIME type from content. ''' ),
    ] = BehaviorTristate.AsNeeded
    mimetype_detectors_order: __.typx.Annotated[
        __.cabc.Sequence[ str ],
        __.ddoc.Doc(
            ''' Order in which MIME type detectors should be applied. ''' ),
    ] = ( 'magic', 'puremagic' )
    mimetype_on_detect_failure: __.typx.Annotated[
        DetectFailureActions,
        __.ddoc.Doc( ''' Action to take on MIME type detection failure. ''' ),
    ] = DetectFailureActions.Default
    on_decode_error: __.typx.Annotated[
        str,
        __.ddoc.Doc(
            ''' Response to charset decoding errors.

                Standard values are 'ignore', 'replace', and 'strict'.
                Can also be any other name which has been registered via
                the 'register_error' function in the Python standard library
                'codecs' module.
            ''' ),
    ] = 'strict'
    text_validate: __.typx.Annotated[
        BehaviorTristate,
        __.ddoc.Doc( ''' When to validate text. ''' ),
    ] = BehaviorTristate.AsNeeded
    text_validate_confidence: __.typx.Annotated[
        float,
        __.ddoc.Doc( ''' Minimum confidence to skip text validation. ''' ),
    ] = 0.80
    trial_codecs: __.typx.Annotated[
        __.cabc.Sequence[ str | CodecSpecifiers ],
        __.ddoc.Doc( ''' Sequence of codec names or specifiers. ''' ),
    ] = ( CodecSpecifiers.FromInference, CodecSpecifiers.UserSupplement )
    trial_decode: __.typx.Annotated[
        BehaviorTristate,
        __.ddoc.Doc(
            ''' When to perform trial decode of content with charset. ''' ),
    ] = BehaviorTristate.AsNeeded
    trial_decode_confidence: __.typx.Annotated[
        float, __.ddoc.Doc( ''' Minimum confidence to skip trial decode. ''')
    ] = 0.80


BehaviorsArgument: __.typx.TypeAlias = __.typx.Annotated[
    Behaviors,
    __.ddoc.Doc(
        ''' Configuration for detection and inference behaviors. ''' ),
]


BEHAVIORS_DEFAULT = Behaviors( )


class CharsetResult( __.immut.DataclassObject ):
    ''' Character set encoding with detection confidence. '''

    charset: __.typx.Annotated[
        __.typx.Optional[ str ],
        __.ddoc.Doc(
            ''' Detected character set encoding. May be ``None``.''' ),
    ]
    confidence: __.typx.Annotated[
        float, __.ddoc.Doc( ''' Detection confidence from 0.0 to 1.0. ''' )
    ]


class MimetypeResult( __.immut.DataclassObject ):
    ''' MIME type with detection confidence. '''

    mimetype: __.typx.Annotated[
        str, __.ddoc.Doc( ''' Detected MIME type. ''' )
    ]
    confidence: __.typx.Annotated[
        float, __.ddoc.Doc( ''' Detection confidence from 0.0 to 1.0. ''' )
    ]


def confidence_from_bytes_quantity(
    content: _nomina.Content, behaviors: Behaviors = BEHAVIORS_DEFAULT
) -> float:
    return min(
        1.0, len( content ) / behaviors.bytes_quantity_confidence_divisor )
