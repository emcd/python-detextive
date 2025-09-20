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
from . import core as _core
from . import exceptions as _exceptions
from . import inference as _inference
from . import mimetypes as _mimetypes
from . import nomina as _nomina
from . import validation as _validation

from .core import ( # isort: skip
    BEHAVIORS_DEFAULT as            _BEHAVIORS_DEFAULT,
    CHARSET_DEFAULT as              _CHARSET_DEFAULT,
    MIMETYPE_DEFAULT as             _MIMETYPE_DEFAULT,
    BehaviorTristate as             _BehaviorTristate,
    BehaviorsArgument as            _BehaviorsArgument,
    CharsetResult as                _CharsetResult,
)


def decode( # noqa: PLR0913
    content: _nomina.Content, /, *,
    behaviors: _BehaviorsArgument = _BEHAVIORS_DEFAULT,
    profile: _validation.ProfileArgument = _validation.PROFILE_TEXTUAL,
    charset_default: _nomina.CharsetDefaultArgument = _CHARSET_DEFAULT,
    mimetype_default: _nomina.MimetypeDefaultArgument = _MIMETYPE_DEFAULT,
    http_content_type: _nomina.HttpContentTypeArgument = __.absent,
    location: _nomina.LocationArgument = __.absent,
    charset_supplement: _nomina.CharsetSupplementArgument = __.absent,
    mimetype_supplement: _nomina.MimetypeSupplementArgument = __.absent,
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
                charset_default = charset_default,
                mimetype_default = mimetype_default,
                http_content_type = http_content_type,
                charset_supplement = charset_supplement,
                mimetype_supplement = mimetype_supplement,
                location = location ) )
    except _exceptions.Omnierror:
        charset = (
            'utf-8-sig' if __.is_absent( charset_supplement )
            else charset_supplement )
        confidence = _core.confidence_from_bytes_quantity( content, behaviors )
        charset_result = _CharsetResult(
            charset = charset, confidence = confidence )
    else:
        if (    charset_result.charset is None
            and not _mimetypes.is_textual_mimetype( mimetype_result.mimetype )
        ): raise _exceptions.ContentDecodeImpossibility( location = location )
    text, result = _charsets.attempt_decodes(
        content,
        behaviors = behaviors,
        inference = (
            'utf-8-sig' if charset_result.charset is None
            else charset_result.charset ),
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
