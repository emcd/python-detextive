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
from . import core as _core
from . import exceptions as _exceptions
from . import nomina as _nomina

from .core import ( # isort: skip
    BEHAVIORS_DEFAULT as        _BEHAVIORS_DEFAULT,
    BehaviorTristate as         _BehaviorTristate,
    Behaviors as                _Behaviors,
    CharsetResult as            _CharsetResult,
    CodecSpecifiers as          _CodecSpecifiers,
)


def attempt_decodes(  # noqa: C901,PLR0912,PLR0913,PLR0915
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = _BEHAVIORS_DEFAULT,
    inference: __.Absential[ str ] = __.absent,
    supplement: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
    validator: __.Absential[
        __.cabc.Callable[ [ str, _CharsetResult ], None ]
    ] = __.absent,
) -> tuple[ str, _CharsetResult ]:
    ''' Attempts to decode content with various character sets.

        Will try character sets in the order specified by the trial codecs
        listed on the behaviors object.
    '''
    confidence = _core.confidence_from_bytes_quantity(
        content, behaviors = behaviors )
    on_decode_error = behaviors.on_decode_error
    trials: set[ str ] = set( )
    for codec in behaviors.trial_codecs:
        match codec:
            case _CodecSpecifiers.FromInference:
                if __.is_absent( inference ): continue
                charset = inference
            case _CodecSpecifiers.OsDefault:
                charset = discover_os_charset_default( )
            case _CodecSpecifiers.PythonDefault:
                charset = __.locale.getpreferredencoding( )
            case _CodecSpecifiers.UserSupplement:
                if __.is_absent( supplement ): continue
                charset = supplement
            case str( ): charset = codec
            case _: continue
        charset = normalize_charset(
            charset, bom_cognizant = behaviors.remove_bom )
        if charset in trials: continue
        try: text = content.decode( charset, errors = on_decode_error )
        except UnicodeDecodeError: continue
        finally: trials.add( charset )
        result = _CharsetResult( charset = charset, confidence = confidence )
        if not __.is_absent( validator ):
            try: validator( text, result )
            except _exceptions.TextInvalidity: continue
        return text, result
    raise _exceptions.ContentDecodeFailure(
        charset = tuple( trials ), location = location )


def discover_os_charset_default( ) -> str:
    ''' Discovers default character set encoding from operating system. '''
    discoverer = getattr(
        __.locale, 'getencoding', __.sys.getfilesystemencoding )
    return normalize_charset( discoverer( ) )


def normalize_charset( charset: str, bom_cognizant: bool = False ) -> str:
    ''' Normalizes character set encoding names. '''
    charset_ = __.codecs.lookup( charset ).name
    if bom_cognizant and charset_ == 'utf-8': return 'utf-8-sig'
    return charset_


def trial_decode_as_confident( # noqa: PLR0913
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = _BEHAVIORS_DEFAULT,
    inference: __.Absential[ str ] = __.absent,
    confidence: float = 0.0,
    supplement: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> _CharsetResult:
    ''' Performs trial decode of content.

        Considers desired trial decode behavior and detection confidence.
    '''
    nomargs: __.NominativeArguments = dict(
        behaviors = behaviors,
        inference = inference,
        supplement = supplement,
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
    return _CharsetResult( charset = inference, confidence = confidence )
