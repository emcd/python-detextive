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


''' Management of bytes array decoding via trial character sets. '''


from . import __
from . import exceptions as _exceptions
from . import nomina as _nomina

from .behaviors import ( # isort: skip
    BEHAVIORS_DEFAULT as    _BEHAVIORS_DEFAULT,
    BehaviorTristate as     _BehaviorTristate,
    Behaviors as            _Behaviors,
    CodecSpecifiers as      _CodecSpecifiers,
)


def attempt_decodes(
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = _BEHAVIORS_DEFAULT,
    charset_inference: __.Absential[ str ] = __.absent,
    charset_default: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> tuple[ str, str ]:
    on_decode_error = behaviors.charset_on_decode_error
    trials: list[ str ] = [ ]
    for codec in behaviors.charset_trial_codecs:
        match codec:
            case _CodecSpecifiers.FromInference:
                if __.is_absent( charset_inference ): continue
                charset = charset_inference
            case _CodecSpecifiers.OsDefault:
                charset = discover_os_charset_default( )
            case _CodecSpecifiers.PythonDefault:
                charset = __.locale.getpreferredencoding( )
            case _CodecSpecifiers.UserDefault:
                if __.is_absent( charset_default ): continue
                charset = charset_default
            case str( ): charset = codec
        try: text = content.decode( charset, errors = on_decode_error )
        except UnicodeDecodeError:
            trials.append( charset )
            continue
        return text, charset
    raise _exceptions.ContentDecodeFailure(
        charset = trials, location = location )


def discover_os_charset_default( ) -> str:
    discoverer = getattr(
        __.locale, 'getencoding', __.sys.getfilesystemencoding )
    return discoverer( )


def trial_decode_as_mandatory(
    content: _nomina.Content, /,
    behaviors: _Behaviors, *,
    charset_inference: __.Absential[ __.typx.Optional[ str ] ] = __.absent,
    charset_default: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> __.Absential[ __.typx.Optional[ str ] ]:
    nomargs: __.NominativeArguments = dict(
        behaviors = behaviors,
        charset_default = charset_default,
        location = location )
    if charset_inference is not None:
        nomargs[ 'charset_inference' ] = charset_inference
    match behaviors.charset_trial_decode:
        case _BehaviorTristate.Always:
            _, charset = attempt_decodes( content, **nomargs )
            return charset
        case _: return charset_inference


def trial_decode_as_necessary(
    content: _nomina.Content, /,
    behaviors: _Behaviors, *,
    charset_inference: __.Absential[ __.typx.Optional[ str ] ] = __.absent,
    charset_default: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> __.Absential[ __.typx.Optional[ str ] ]:
    nomargs: __.NominativeArguments = dict(
        behaviors = behaviors,
        charset_default = charset_default,
        location = location )
    if charset_inference is not None:
        nomargs[ 'charset_inference' ] = charset_inference
    match behaviors.charset_trial_decode:
        case _BehaviorTristate.Never: return charset_inference
        case _:
            _, charset = attempt_decodes( content, **nomargs )
            return charset
