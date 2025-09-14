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
from . import exceptions as _exceptions
from . import inference as _inference
from . import mimetypes as _mimetypes
from . import nomina as _nomina
from . import validation as _validation

from .core import ( # isort: skip
    BEHAVIORS_DEFAULT as            _BEHAVIORS_DEFAULT,
    BehaviorTristate as             _BehaviorTristate,
    Behaviors as                    _Behaviors,
    Result as                       _Result,
    confidence_from_quantity as     _confidence_from_quantity,
)


def decode( # noqa: PLR0913
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = _BEHAVIORS_DEFAULT,
    profile: _validation.Profile = _validation.PROFILE_TEXTUAL,
    http_content_type: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
    charset_supplement: str = 'utf-8-sig',
    mimetype_supplement: __.Absential[ str ] = __.absent,
) -> str:
    ''' Decodes bytes array to Unicode text. '''
    if content == b'': return ''
    behaviors_ = __.dcls.replace(
        behaviors, trial_decode = _BehaviorTristate.Never )
    try:
        mimetype_result, charset_result = (
            _inference.infer_mimetype_charset_confidence(
                content,
                behaviors = behaviors_,
                http_content_type = http_content_type,
                charset_supplement = charset_supplement,
                mimetype_supplement = mimetype_supplement,
                location = location ) )
    except _exceptions.Omnierror:
        confidence = _confidence_from_quantity( content, behaviors )
        charset_result = _Result(
            value = charset_supplement, confidence = confidence )
    else:
        if (    charset_result is None
            and not _mimetypes.is_textual_mimetype( mimetype_result.value )
        ): raise _exceptions.ContentDecodeImpossibility( location = location )
    text, result = _charsets.attempt_decodes(
        content,
        behaviors = behaviors,
        inference = (
            'utf-8-sig' if charset_result is None else charset_result.value ),
        supplement = charset_supplement,
        location = location )
    should_validate = False
    match behaviors.text_validate:
        case _BehaviorTristate.Always:
            should_validate = True
        case _BehaviorTristate.AsNeeded:
            should_validate = (
                result.confidence < behaviors.text_validate_confidence )
        case _BehaviorTristate.Never: pass
    if should_validate and not profile( text ):
        raise _exceptions.TextInvalidity( location = location )
    return text
