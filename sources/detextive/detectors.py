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

from .core import ( # isort: skip
    BEHAVIORS_DEFAULT as            _BEHAVIORS_DEFAULT,
    BehaviorTristate as             _BehaviorTristate,
    Behaviors as                    _Behaviors,
    Result as                       _Result,
    confidence_from_quantity as     _confidence_from_quantity,
)


_BOM_BYTES = b'\xef\xbb\xbf'


def detect_charset(
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = _BEHAVIORS_DEFAULT,
    supplement: __.Absential[ str ] = __.absent,
    mimetype: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> __.typx.Optional[ str ]:
    ''' Detects character set. '''
    result = detect_charset_confidence(
        content,
        behaviors = behaviors,
        supplement = supplement,
        mimetype = mimetype,
        location = location )
    if result is None: return None
    return result.value


def detect_charset_confidence(
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = _BEHAVIORS_DEFAULT,
    supplement: __.Absential[ str ] = __.absent,
    mimetype: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> __.typx.Optional[ _Result ]:
    ''' Detects character set candidates with confidence scores. '''
    if b'' == content: return _Result( value = 'utf-8', confidence = 1.0 )
    # TODO: Use 'charset-normalizer', if available.
    result = __.chardet.detect( content )
    charset, confidence = result[ 'encoding' ], result[ 'confidence' ]
    nomargs: __.NominativeArguments = dict(
        behaviors = behaviors,
        confidence = confidence,
        supplement = supplement,
        location = location )
    if charset is None:
        if __.is_absent( mimetype ): return None
        if _mimetypes.is_textual_mimetype( mimetype ):
            result = _charsets.trial_decode_as_necessary( content, **nomargs )
            return _normalize_charset_detection( content, behaviors, result )
        return None
    charset = behaviors.charset_promotions.get( charset, charset )
    result = _confirm_charset_detection(
        content, behaviors, charset,
        confidence = confidence, supplement = supplement, location = location )
    return _normalize_charset_detection( content, behaviors, result )


def detect_mimetype(
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = _BEHAVIORS_DEFAULT,
    charset: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> str:
    ''' Detects most probable MIME type. '''
    nomargs: __.NominativeArguments = dict(
        behaviors = behaviors, charset = charset, location = location )
    result = detect_mimetype_confidence( content, **nomargs )
    return result.value


def detect_mimetype_confidence(
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = _BEHAVIORS_DEFAULT,
    charset: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> _Result:
    ''' Detects MIME type candidates with confidence scores. '''
    # TODO: Use 'magic', if available.
    error = _exceptions.MimetypeDetectFailure( location = location )
    try: mimetype = __.puremagic.from_string( content, mime = True )
    except ( __.puremagic.PureError, ValueError ):
        if __.is_absent( charset ): raise error from None
        mimetype = _detect_mimetype_from_charset(
            content, behaviors, charset, location = location )
        return _Result( value = mimetype, confidence = 1.0 )
    confidence = _confidence_from_quantity( content, behaviors = behaviors )
    return _Result( value = mimetype, confidence = confidence )


def _confirm_charset_detection( # noqa: PLR0913
    content: _nomina.Content,
    behaviors: _Behaviors,
    charset: str, /, *,
    confidence: float = 1.0,
    supplement: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> _Result:
    nomargs: __.NominativeArguments = dict(
        behaviors = behaviors,
        supplement = supplement,
        inference = charset,
        confidence = confidence,
        location = location )
    if charset.startswith( 'utf-' ):
        return _charsets.trial_decode_as_confident( content, **nomargs )
    nomargs: __.NominativeArguments = dict(
        behaviors = behaviors,
        inference = 'utf-8-sig',
        supplement = supplement,
        location = location )
    result = _Result( value = charset, confidence = confidence )
    match behaviors.trial_decode:
        case _BehaviorTristate.Never: return result
        # Shake out false positives, like 'MacRoman'.
        case _:
            if charset == _charsets.discover_os_charset_default( ):
                # Allow 'windows-1252', etc..., as appropriate.
                return result
            try: _, result_ = _charsets.attempt_decodes( content, **nomargs )
            except _exceptions.ContentDecodeFailure: return result
            if charset == result_.value: return result
            return result_


def _detect_mimetype_from_charset(
    content: _nomina.Content,
    behaviors: _Behaviors,
    charset: str, /, *,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> str:
    Error = _exceptions.MimetypeDetectFailure
    nomargs: __.NominativeArguments = dict(
        behaviors = behaviors, inference = charset, location = location )
    try: _charsets.trial_decode_as_confident( content, **nomargs )
    except _exceptions.ContentDecodeFailure:
        raise Error( location = location ) from None
    return 'text/plain'


def _normalize_charset_detection(
    content: _nomina.Content, behaviors: _Behaviors, result: _Result
) -> _Result:
    charset = result.value
    if charset == 'utf-8-sig' and not content.startswith( _BOM_BYTES ):
        charset = 'utf-8'
    return _Result( value = charset, confidence = result.confidence )
