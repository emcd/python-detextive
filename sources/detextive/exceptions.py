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


''' Family of exceptions for package API. '''


from . import __
from . import nomina as _nomina


class Omniexception(
    __.immut.Object, BaseException,
    instances_mutables = ( '__cause__', '__context__' ),
    instances_visibles = (
        '__cause__', '__context__', __.is_public_identifier ),
):
    ''' Base for all exceptions raised by package API. '''


class Omnierror( Omniexception, Exception ):
    ''' Base for error exceptions raised by package API. '''


class CharsetDetectFailure( Omnierror, TypeError, ValueError ):

    def __init__(
        self, location: __.Absential[ _nomina.Location ] = __.absent
    ) -> None:
        message = "Could not detect character set for content"
        if not __.is_absent( location ):
            message = f"{message} at '{location}'"
        super( ).__init__( f"{message}." )


class CharsetInferFailure( Omnierror, TypeError, ValueError ):

    def __init__(
        self, location: __.Absential[ _nomina.Location ] = __.absent
    ) -> None:
        message = "Could not infer character set for content"
        if not __.is_absent( location ):
            message = f"{message} at '{location}'"
        super( ).__init__( f"{message}." )


class ContentDecodeImpossibility( Omnierror, TypeError, ValueError ):

    def __init__(
        self, location: __.Absential[ _nomina.Location ] = __.absent
    ) -> None:
        message = "Could not decode probable non-textual content"
        if not __.is_absent( location ):
            message = f"{message} at '{location}'"
        super( ).__init__( f"{message}." )


class ContentDecodeFailure( Omnierror, UnicodeError ):

    def __init__(
        self,
        charset: str | __.cabc.Sequence[ str ],
        location: __.Absential[ _nomina.Location ] = __.absent,
    ) -> None:
        message = "Could not decode content"
        if not __.is_absent( location ):
            message = f"{message} at '{location}'"
        if isinstance( charset, str ): charset = ( charset, )
        charsets = ', '.join( f"'{charset_}'" for charset_ in charset )
        message = f"{message} with character sets {charsets}"
        super( ).__init__( f"{message}." )


class MimetypeDetectFailure( Omnierror, TypeError, ValueError ):

    def __init__(
        self, location: __.Absential[ _nomina.Location ] = __.absent
    ) -> None:
        # TODO: Add 'reason' argument.
        message = "Could not detect MIME type for content"
        if not __.is_absent( location ):
            message = f"{message} at '{location}'"
        super( ).__init__( f"{message}." )


class MimetypeInferFailure( Omnierror, TypeError, ValueError ):

    def __init__(
        self, location: __.Absential[ _nomina.Location ] = __.absent
    ) -> None:
        message = "Could not infer MIME type for content"
        if not __.is_absent( location ):
            message = f"{message} at '{location}'"
        super( ).__init__( f"{message}." )


class TextInvalidity( Omnierror, TypeError, ValueError ):

    def __init__(
        self, location: __.Absential[ _nomina.Location ] = __.absent
    ) -> None:
        # TODO: Add 'reason' argument.
        message = "Text is not valid"
        if not __.is_absent( location ):
            message = f"{message} at '{location}'"
        super( ).__init__( f"{message}." )


class TextualMimetypeInvalidity( Omnierror, ValueError ):

    def __init__(
        self,
        mimetype: str,
        location: __.Absential[ _nomina.Location ] = __.absent,
    ) -> None:
        message = "MIME type '{mimetype}' is not textual for content"
        if not __.is_absent( location ):
            message = f"{message} at '{location}'"
        super( ).__init__( f"{message}." )
