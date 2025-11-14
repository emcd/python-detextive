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
    MIMETYPE_DEFAULT as             _MIMETYPE_DEFAULT,
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
    mimetype_default: _nomina.MimetypeDefaultArgument = _MIMETYPE_DEFAULT,
    http_content_type: _nomina.HttpContentTypeArgument = __.absent,
    location: _nomina.LocationArgument = __.absent,
    charset_supplement: _nomina.CharsetSupplementArgument = __.absent,
    mimetype_supplement: _nomina.MimetypeSupplementArgument = __.absent,
) -> str:
    ''' Decodes bytes array to Unicode text. '''
    # TODO: Deprecation warnings for 'mimetype_*' arguments.
    if content == b'': return ''
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
    return _attempt_decodes(
        content, result,
        behaviors = behaviors,
        profile = profile,
        supplement = charset_supplement,
        location = location )


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


def _append_charset(
    permissives: list[ str ],
    restrictives: list[ str ],
    charset: str,
    bom_cognizant: bool,
) -> None:
    charset_ = _charsets.normalize_charset(
        charset, bom_cognizant = bom_cognizant )
    if _charsets.is_permissive_charset( charset_ ):
        if charset_ in permissives: return
        permissives.append( charset_ )
    else:
        if charset_ in restrictives: return
        restrictives.append( charset_ )


def _attempt_decodes(  # noqa: PLR0913
    content: _nomina.Content,
    detection: __.Absential[ _CharsetResult ], /, *,
    behaviors: _BehaviorsArgument,
    profile: _validation.ProfileArgument,
    supplement: __.Absential[ str ],
    location: _nomina.LocationArgument,
) -> str:
    error = _exceptions.ContentDecodeImpossibility( location = location )
    permissives, restrictives = _prepare_charsets(
        detection, behaviors = behaviors, supplement = supplement )
    on_decode_error = behaviors.on_decode_error
    # Try restrictive charsets before permissive charsets, since:
    # (1) Restrictive charsets can have decoding errors from invalid byte
    #     sequences.
    # (2) Restrictive charsets can produce shorter strings, if the are
    #     multi-byte encodings. Permissive charsets decoding the same byte
    #     sequences will likly result in mojibake.
    for charset in restrictives:
        try: text = content.decode( charset, errors = on_decode_error )
        except UnicodeDecodeError: continue
        try:
            return _validate_text(
                text, 0.0,
                behaviors = behaviors, profile = profile, location = location )
        except _exceptions.TextInvalidity: continue
    for charset in permissives:
        try: text = content.decode( charset, errors = on_decode_error )
        except UnicodeDecodeError: continue
        try:
            return _validate_text(
                text, 0.0,
                behaviors = behaviors, profile = profile, location = location )
        except _exceptions.TextInvalidity: continue
    raise error


def _prepare_charsets(
    detection: __.Absential[ _CharsetResult ], /, *,
    behaviors: _BehaviorsArgument,
    supplement: __.Absential[ str ],
) -> tuple[ tuple[ str, ... ], tuple[ str, ... ] ]:
    permissives: list[ str ] = [ ]
    restrictives: list[ str ] = [ ]
    os_charset = _charsets.discover_os_charset_default( )
    _append_charset(
        permissives, restrictives, os_charset, behaviors.remove_bom )
    python_charset = __.locale.getpreferredencoding( )
    _append_charset(
        permissives, restrictives, python_charset, behaviors.remove_bom )
    if not __.is_absent( supplement ):
        _prepend_charset(
            permissives, restrictives, supplement, behaviors.remove_bom )
    if not __.is_absent( detection ) and detection.charset is not None:
        # Suspicious charset detections go at end.
        if detection.confidence < behaviors.trial_decode_confidence:
            _append_charset(
                permissives, restrictives, detection.charset,
                behaviors.remove_bom )
        else:
            _prepend_charset(
                permissives, restrictives, detection.charset,
                behaviors.remove_bom )
    return tuple( permissives ), tuple( restrictives )


def _prepend_charset(
    permissives: list[ str ],
    restrictives: list[ str ],
    charset: str,
    bom_cognizant: bool,
) -> None:
    charset_ = _charsets.normalize_charset(
        charset, bom_cognizant = bom_cognizant )
    if _charsets.is_permissive_charset( charset_ ):
        if charset_ in permissives: return
        permissives.insert( 0, charset_ )
    else:
        if charset_ in restrictives: return
        restrictives.insert( 0, charset_ )


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
