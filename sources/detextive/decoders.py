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
from . import lineseparators as _lineseparators
from . import mimetypes as _mimetypes
from . import nomina as _nomina
from . import validation as _validation

from .core import ( # isort: skip
    BEHAVIORS_DEFAULT as            _BEHAVIORS_DEFAULT,
    BehaviorTristate as             _BehaviorTristate,
    BehaviorsArgument as            _BehaviorsArgument,
    CharsetResult as                _CharsetResult,
    CodecSpecifiers as              _CodecSpecifiers,
    MimetypeResult as               _MimetypeResult,
)


_MIMETYPE_DEFAULT_TEXTUAL = 'text/plain'


class DecodeInformResult( __.immut.DataclassObject ):
    ''' Decoded text with supplemental inference metadata. '''

    text: __.typx.Annotated[
        str, __.ddoc.Doc( ''' Decoded text content. ''' )
    ]
    charset: __.typx.Annotated[
        _CharsetResult, __.ddoc.Doc( ''' Charset used for decoding. ''' )
    ]
    mimetype: __.typx.Annotated[
        _MimetypeResult, __.ddoc.Doc( ''' Inferred MIME type metadata. ''' )
    ]
    linesep: __.typx.Annotated[
        __.typx.Optional[ _lineseparators.LineSeparators ],
        __.ddoc.Doc( ''' Detected line separator from content sample. ''' ),
    ]


def decode( # noqa: PLR0913
    content: _nomina.Content, /, *,
    behaviors: _BehaviorsArgument = _BEHAVIORS_DEFAULT,
    profile: _validation.ProfileArgument = _validation.PROFILE_TEXTUAL,
    http_content_type: _nomina.HttpContentTypeArgument = __.absent,
    location: _nomina.LocationArgument = __.absent,
    charset_supplement: _nomina.CharsetSupplementArgument = __.absent,
) -> str:
    ''' Decodes bytes array to Unicode text.

        Uses trial decoding and validation; does not provide default-return
        semantics. The ``charset_supplement`` parameter is a trial hint and
        not a fallback return value.
    '''
    _, httpct_charset = _parse_http_content_type( http_content_type )
    return _decode_content_charset_result(
        content, behaviors, profile,
        httpct_charset = httpct_charset,
        location = location,
        charset_supplement = charset_supplement )[ 0 ]


def decode_inform( # noqa: PLR0913
    content: _nomina.Content, /, *,
    behaviors: _BehaviorsArgument = _BEHAVIORS_DEFAULT,
    profile: _validation.ProfileArgument = _validation.PROFILE_TEXTUAL,
    mimetype_default: _nomina.MimetypeDefaultArgument = (
        _MIMETYPE_DEFAULT_TEXTUAL ),
    http_content_type: _nomina.HttpContentTypeArgument = __.absent,
    location: _nomina.LocationArgument = __.absent,
    charset_supplement: _nomina.CharsetSupplementArgument = __.absent,
) -> DecodeInformResult:
    ''' Decodes bytes and returns supplemental inference metadata. '''
    httpct_mimetype, httpct_charset = (
        _parse_http_content_type( http_content_type ) )
    text, charset_result = _decode_content_charset_result(
        content, behaviors, profile,
        httpct_charset = httpct_charset,
        location = location,
        charset_supplement = charset_supplement )
    mimetype_result = _infer_mimetype(
        content, behaviors,
        mimetype_default = mimetype_default,
        httpct_mimetype = httpct_mimetype,
        location = location,
        charset = charset_result.charset )
    linesep = _lineseparators.LineSeparators.detect_bytes( content )
    return DecodeInformResult(
        text = text,
        charset = charset_result,
        mimetype = mimetype_result,
        linesep = linesep )


def _attempt_decode_http_content_type(
    content: _nomina.Content,
    behaviors: _BehaviorsArgument,
    profile: _validation.ProfileArgument, /, *,
    httpct_charset: __.Absential[ __.typx.Optional[ str ] ],
    location: _nomina.LocationArgument,
) -> __.Absential[ tuple[ str, _CharsetResult ] ]:
    result: __.Absential[ _CharsetResult ] = __.absent
    error = _exceptions.ContentDecodeImpossibility( location = location )
    if httpct_charset is None: raise error
    if __.is_absent( httpct_charset ): return __.absent
    behaviors_ = __.dcls.replace(
        behaviors, trial_codecs = ( _CodecSpecifiers.FromInference, ) )
    try:
        text, result = _charsets.attempt_decodes(
            content,
            behaviors = behaviors_,
            inference = httpct_charset,
            location = location )
    except _exceptions.ContentDecodeFailure: return __.absent
    # Allow other errors propagate.
    if not __.is_absent( text ) and not __.is_absent( result ):
        text = _validate_text(
            text, result.confidence,
            behaviors = behaviors, profile = profile, location = location )
        return text, result
    return __.absent


def _decode_content_charset_result( # noqa: PLR0913
    content: _nomina.Content,
    behaviors: _BehaviorsArgument,
    profile: _validation.ProfileArgument, /, *,
    httpct_charset: __.Absential[ __.typx.Optional[ str ] ],
    location: _nomina.LocationArgument,
    charset_supplement: _nomina.CharsetSupplementArgument,
) -> tuple[ str, _CharsetResult ]:
    if content == b'':
        return '', _CharsetResult( charset = 'utf-8', confidence = 1.0 )
    charset: __.Absential[ str ] = __.absent
    result: __.Absential[ _CharsetResult ] = __.absent
    httpct_result: __.Absential[ tuple[ str, _CharsetResult ] ] = __.absent
    httpct_result = _attempt_decode_http_content_type(
        content, behaviors, profile,
        httpct_charset = httpct_charset, location = location )
    if not __.is_absent( httpct_result ): return httpct_result
    if __.is_absent( result ):
        behaviors_ = __.dcls.replace(
            behaviors, trial_decode = _BehaviorTristate.Never )
        with __.ctxl.suppress( _exceptions.CharsetDetectFailure ):
            result = _detectors.detect_charset_confidence(
                content,
                behaviors = behaviors_,
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
        validator = validator )


def _infer_mimetype( # noqa: PLR0913
    content: _nomina.Content,
    behaviors: _BehaviorsArgument, /, *,
    mimetype_default: _nomina.MimetypeDefaultArgument,
    httpct_mimetype: __.Absential[ str ],
    location: _nomina.LocationArgument,
    charset: __.typx.Optional[ str ],
) -> _MimetypeResult:
    charset_ = __.absent if charset is None else charset
    if (    not __.is_absent( httpct_mimetype )
        and _mimetypes.is_textual_mimetype( httpct_mimetype )
    ):
        return _MimetypeResult( mimetype = httpct_mimetype, confidence = 0.9 )
    result: __.Absential[ _MimetypeResult ] = __.absent
    if not __.is_absent( location ):
        mimetype = _mimetypes.mimetype_from_location( location )
        if (    not __.is_absent( mimetype )
            and _mimetypes.is_textual_mimetype( mimetype )
        ):
            return _MimetypeResult( mimetype = mimetype, confidence = 0.9 )
    if behaviors.mimetype_detect is not _BehaviorTristate.Never:
        result = _detectors.detect_mimetype_confidence(
            content,
            behaviors = behaviors,
            default = mimetype_default,
            charset = charset_,
            location = location )
    if __.is_absent( result ):
        return _MimetypeResult( mimetype = mimetype_default, confidence = 1.0 )
    if _mimetypes.is_textual_mimetype( result.mimetype ): return result
    return _MimetypeResult( mimetype = mimetype_default, confidence = 1.0 )


def _parse_http_content_type(
    http_content_type: _nomina.HttpContentTypeArgument
) -> tuple[ __.Absential[ str ], __.Absential[ __.typx.Optional[ str ] ] ]:
    if __.is_absent( http_content_type ):
        return __.absent, __.absent
    return _inference.parse_http_content_type( http_content_type )


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
