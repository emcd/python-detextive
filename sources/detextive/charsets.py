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

from .core import ( # isort: skip
    BEHAVIORS_DEFAULT as        _BEHAVIORS_DEFAULT,
    BehaviorTristate as         _BehaviorTristate,
    Behaviors as                _Behaviors,
    CodecSpecifiers as          _CodecSpecifiers,
    Result as                   _Result,
    confidence_from_quantity as _confidence_from_quantity,
)


def attempt_decodes(
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = _BEHAVIORS_DEFAULT,
    inference: __.Absential[ str ] = __.absent,
    default: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> tuple[ str, _Result ]:
    confidence = _confidence_from_quantity( content, behaviors = behaviors )
    on_decode_error = behaviors.on_decode_error
    trials: list[ str ] = [ ]
    for codec in behaviors.trial_codecs:
        match codec:
            case _CodecSpecifiers.FromInference:
                if __.is_absent( inference ): continue
                charset = inference
            case _CodecSpecifiers.OsDefault:
                charset = discover_os_charset_default( )
            case _CodecSpecifiers.PythonDefault:
                charset = __.locale.getpreferredencoding( )
            case _CodecSpecifiers.UserDefault:
                if __.is_absent( default ): continue
                charset = default
            case str( ): charset = codec
            case _: continue
        try: text = content.decode( charset, errors = on_decode_error )
        except UnicodeDecodeError:
            trials.append( charset )
            continue
        return text, _Result( value = charset, confidence = confidence )
    raise _exceptions.ContentDecodeFailure(
        charset = trials, location = location )


def discover_os_charset_default( ) -> str:
    discoverer = getattr(
        __.locale, 'getencoding', __.sys.getfilesystemencoding )
    return discoverer( )


def trial_decode_as_confident( # noqa: PLR0913
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = _BEHAVIORS_DEFAULT,
    inference: __.Absential[ str ] = __.absent,
    confidence: float = 1.0,
    default: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> _Result:
    nomargs: __.NominativeArguments = dict(
        behaviors = behaviors,
        default = default, inference = inference,
        location = location )
    should_decode = False
    match behaviors.trial_decode:
        case _BehaviorTristate.Always: should_decode = True
        case _BehaviorTristate.AsNeeded:
            should_decode = confidence < behaviors.trial_decode_confidence
        case _BehaviorTristate.Never: pass
    if should_decode:
        _, result = attempt_decodes( content, **nomargs )
        return result
    if __.is_absent( inference ):
        raise _exceptions.CharsetDetectFailure( location = location )
    return _Result( value = inference, confidence = confidence )
