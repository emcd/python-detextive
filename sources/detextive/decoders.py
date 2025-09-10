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
from . import nomina as _nomina
from . import validation as _validation

from .interfaces import ( # isort: skip
    BEHAVIORS_DEFAULT as            _BEHAVIORS_DEFAULT,
    BehaviorTristate as             _BehaviorTristate,
    Behaviors as                    _Behaviors,
)


def decode( # noqa: PLR0913
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = _BEHAVIORS_DEFAULT,
    profile: _validation.Profile = _validation.PROFILE_TEXTUAL,
    http_content_type: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
    charset_default: __.Absential[ str ] = __.absent,
    # mimetype_default: __.Absential[ str ] = __.absent,
) -> str:
    ''' Decodes bytes array to Unicode text. '''
    behaviors_ = __.dcls.replace(
        behaviors, charset_trial_decode = _BehaviorTristate.Never )
    charset = _inference.infer_charset(
        content,
        behaviors = behaviors_,
        http_content_type = http_content_type,
        location = location )
    if charset is None:
        raise _exceptions.ContentDecodeImpossibility( location = location )
    text, _ = _charsets.attempt_decodes(
        content,
        behaviors = behaviors,
        charset_default = charset_default,
        charset_inference = charset,
        location = location )
    match behaviors.text_validate:
        case _BehaviorTristate.Always:
            if not profile( text ):
                raise _exceptions.TextInvalidity( location = location )
        # TODO: Handle 'AsNeeded' case based on confidence.
        case _: pass
    return text
