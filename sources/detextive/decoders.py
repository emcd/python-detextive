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


''' Conversion of bytes arrays to Unicode text. '''


from . import __
from . import charsets as _charsets
from . import detectors as _detectors
from . import exceptions as _exceptions
from . import inference as _inference
from . import nomina as _nomina
from . import validation as _validation

from .core import ( # isort: skip
    BEHAVIORS_DEFAULT as            _BEHAVIORS_DEFAULT,
    CHARSET_DEFAULT as              _CHARSET_DEFAULT,
    BehaviorTristate as             _BehaviorTristate,
    BehaviorsArgument as            _BehaviorsArgument,
    CharsetResult as                _CharsetResult,
    CodecSpecifiers as              _CodecSpecifiers,
)


def decode( # noqa: PLR0913
    content: _nomina.Content, /, *,
    behaviors: _BehaviorsArgument = _BEHAVIORS_DEFAULT,
    profile: _validation.ProfileArgument = _validation.PROFILE_TEXTUAL,
    charset_default: _nomina.CharsetDefaultArgument = _CHARSET_DEFAULT,
    http_content_type: _nomina.HttpContentTypeArgument = __.absent,
    location: _nomina.LocationArgument = __.absent,
    charset_supplement: _nomina.CharsetSupplementArgument = __.absent,
) -> str:
    ''' Decodes bytes array to Unicode text. '''
    if content == b'': return ''
    charset: __.Absential[ str ] = __.absent
    result: __.Absential[ _CharsetResult ] = __.absent
    text: __.Absential[ str ] = __.absent
    if not __.is_absent( http_content_type ):
        text = _attempt_decode_http_content_type(
            content, http_content_type,
            behaviors = behaviors, profile = profile, location = location )
        if not __.is_absent( text ): return text
    if __.is_absent( result ):
        behaviors_ = __.dcls.replace(
            behaviors, trial_decode = _BehaviorTristate.Never )
        with __.ctxl.suppress( _exceptions.CharsetDetectFailure ):
            result = _detectors.detect_charset_confidence(
                content,
                behaviors = behaviors_,
                default = charset_default,
                supplement = charset_supplement,
                location = location )
            if (    result.charset
                and result.confidence >= behaviors.trial_decode_confidence
            ): charset = result.charset
    validator = __.funct.partial(
        _validate_text_in_decode_attempt,
        behaviors = behaviors,
        profile = profile,
        location = location )
    return _charsets.attempt_decodes(
        content,
        behaviors = behaviors,
        inference = charset,
        supplement = charset_supplement,
        location = location,
        validator = validator )[ 0 ]


def _attempt_decode_http_content_type(
    content: _nomina.Content,
    http_content_type: str, /, *,
    behaviors: _BehaviorsArgument,
    profile: _validation.ProfileArgument,
    location: _nomina.LocationArgument,
) -> __.Absential[ str ]:
    charset: __.Absential[ __.typx.Optional[ str ] ] = __.absent
    result: __.Absential[ _CharsetResult ] = __.absent
    error = _exceptions.ContentDecodeImpossibility( location = location )
    _, charset = _inference.parse_http_content_type( http_content_type )
    if charset is None: raise error
    if __.is_absent( charset ): return __.absent
    behaviors_ = __.dcls.replace(
        behaviors, trial_codecs = ( _CodecSpecifiers.FromInference, ) )
    try:
        text, result = _charsets.attempt_decodes(
            content,
            behaviors = behaviors_, inference = charset, location = location )
    except _exceptions.ContentDecodeFailure: return __.absent
    # Allow other errors propagate.
    if not __.is_absent( text ) and not __.is_absent( result ):
        return _validate_text(
            text, result.confidence,
            behaviors = behaviors, profile = profile, location = location )
    return __.absent


def _validate_text(
    text: str, confidence: float, /, *,
    behaviors: _BehaviorsArgument,
    profile: _validation.ProfileArgument,
    location: _nomina.LocationArgument,
) -> str:
    error = _exceptions.TextInvalidity( location = location )
    should_validate = False
    match behaviors.text_validate:
        case _BehaviorTristate.Always:
            should_validate = True
        case _BehaviorTristate.AsNeeded:
            should_validate = confidence < behaviors.text_validate_confidence
        case _BehaviorTristate.Never: pass
    if should_validate and not profile( text ): raise error
    return text


def _validate_text_in_decode_attempt(
    text: str, result: _CharsetResult, /, *,
    behaviors: _BehaviorsArgument,
    profile: _validation.ProfileArgument,
    location: _nomina.LocationArgument,
) -> None:
    _validate_text(
        text, 0.0,
        behaviors = behaviors,
        profile = profile,
        location = location )
