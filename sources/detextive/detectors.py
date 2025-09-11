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


''' Core detection function implementations. '''


from . import __
from . import charsets as _charsets
from . import exceptions as _exceptions
from . import mimetypes as _mimetypes
from . import nomina as _nomina

from .behaviors import ( # isort: skip
    BEHAVIORS_DEFAULT as            _BEHAVIORS_DEFAULT,
    BehaviorTristate as             _BehaviorTristate,
    Behaviors as                    _Behaviors,
)


def detect_charset( # noqa: PLR0911
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = _BEHAVIORS_DEFAULT,
    default: __.Absential[ str ] = __.absent,
    mimetype: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> __.typx.Optional[ str ]:
    ''' Detects character set. '''
    # TODO: Use 'charset-normalizer', if available.
    # TODO? Return confidence from detector.
    ''' Detects character set. '''
    result = __.chardet.detect( content )
    charset = result[ 'encoding' ]
    nomargs: __.NominativeArguments = dict(
        behaviors = behaviors, charset_default = default, location = location )
    if charset is None:
        if __.is_absent( mimetype ): return None
        if _mimetypes.is_textual_mimetype( mimetype ):
            charset = _charsets.trial_decode_as_necessary( content, **nomargs )
            if __.is_absent( charset ): return None
            return charset
        return None
    charset = behaviors.charset_promotions.get( charset, charset )
    nomargs_: __.NominativeArguments = dict(
        charset_inference = charset, **nomargs )
    if charset.startswith( 'utf-' ):
        charset = _charsets.trial_decode_as_mandatory( content, **nomargs_ )
        return __.typx.cast( str, charset )
    match behaviors.charset_trial_decode:
        case _BehaviorTristate.Never: return charset
        # Shake out false positives, like 'MacRoman'.
        case _:
            if charset == _charsets.discover_os_charset_default( ):
                # Allow 'windows-1252', etc..., as appropriate.
                return charset
            try: _, charset_ = _charsets.attempt_decodes( content, **nomargs )
            except _exceptions.ContentDecodeFailure: return charset
            return charset_


def detect_mimetype(
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = _BEHAVIORS_DEFAULT,
    charset: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> str:
    # TODO: Use 'magic', if available.
    # TODO? Return confidence, based on content length.
    ''' Detects MIME type. '''
    try: return __.puremagic.from_string( content, mime = True )
    except ( __.puremagic.PureError, ValueError ) as exc_magic:
        Error = _exceptions.MimetypeDetectFailure
        # If content is textual, then we can at least return 'text/plain'.
        if not __.is_absent( charset ):
            nomargs: __.NominativeArguments = dict(
                behaviors = behaviors,
                charset_inference = charset,
                location = location )
            try:
                charset_ = _charsets.trial_decode_as_necessary(
                    content, **nomargs )
            except _exceptions.ContentDecodeFailure:
                raise Error( location = location ) from None
            if not __.is_absent( charset_ ): return 'text/plain'
        raise Error( location = location ) from exc_magic
