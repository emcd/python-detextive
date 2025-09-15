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
from . import core as _core
from . import exceptions as _exceptions
from . import mimetypes as _mimetypes
from . import nomina as _nomina
from . import validation as _validation

from .core import ( # isort: skip
    BEHAVIORS_DEFAULT as            _BEHAVIORS_DEFAULT,
    BehaviorTristate as             _BehaviorTristate,
    Behaviors as                    _Behaviors,
    CharsetResult as                _CharsetResult,
    MimetypeResult as               _MimetypeResult,
)


CharsetDetector: __.typx.TypeAlias = __.cabc.Callable[
    [ _nomina.Content, _Behaviors ],
    _CharsetResult | __.types.NotImplementedType
]
MimetypeDetector: __.typx.TypeAlias = __.cabc.Callable[
    [ _nomina.Content, _Behaviors ],
    _MimetypeResult | __.types.NotImplementedType
]


_BOM_BYTES = b'\xef\xbb\xbf'


charset_detectors: __.accret.Dictionary[ str, CharsetDetector ] = (
    __.accret.Dictionary( ) )
mimetype_detectors: __.accret.Dictionary[ str, MimetypeDetector ] = (
    __.accret.Dictionary( ) )


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
    return result.charset


def detect_charset_confidence(
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = _BEHAVIORS_DEFAULT,
    supplement: __.Absential[ str ] = __.absent,
    mimetype: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> _CharsetResult:
    ''' Detects character set candidates with confidence scores. '''
    if b'' == content:
        return _CharsetResult( charset = 'utf-8', confidence = 1.0 )
    for name in behaviors.charset_detectors_order:
        detector = charset_detectors.get( name )
        if detector is None: continue
        result = detector( content, behaviors )
        if result is NotImplemented: continue
        break
    else: raise _exceptions.CharsetDetectFailure( location = location )
    if result.charset is None:
        if __.is_absent( mimetype ): return result
        if _mimetypes.is_textual_mimetype( mimetype ):
            result = _charsets.trial_decode_as_confident(
                content,
                behaviors = behaviors,
                supplement = supplement,
                location = location )
            return _normalize_charset_detection( content, behaviors, result )
        return result
    charset, confidence = result.charset, result.confidence
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
    return result.mimetype


def detect_mimetype_confidence(
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = _BEHAVIORS_DEFAULT,
    charset: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> _MimetypeResult:
    ''' Detects MIME type candidates with confidence scores. '''
    error = _exceptions.MimetypeDetectFailure( location = location )
    for name in behaviors.mimetype_detectors_order:
        detector = mimetype_detectors.get( name )
        if detector is None: continue
        result = detector( content, behaviors )
        if result is NotImplemented: continue
        return result
    if __.is_absent( charset ): raise error
    return _detect_mimetype_from_charset(
        content, behaviors, charset, location = location )


def _confirm_charset_detection( # noqa: PLR0913
    content: _nomina.Content,
    behaviors: _Behaviors,
    charset: str, /, *,
    confidence: float = 1.0,
    supplement: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> _CharsetResult:
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
    result = _CharsetResult( charset = charset, confidence = confidence )
    match behaviors.trial_decode:
        case _BehaviorTristate.Never: return result
        # Shake out false positives, like 'MacRoman'.
        case _:
            if charset == _charsets.discover_os_charset_default( ):
                # Allow 'windows-1252', etc..., as appropriate.
                return result
            try: _, result_ = _charsets.attempt_decodes( content, **nomargs )
            except _exceptions.ContentDecodeFailure: return result
            if charset == result_.charset: return result
            return result_


def _detect_mimetype_from_charset(
    content: _nomina.Content,
    behaviors: _Behaviors,
    charset: str, /, *,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> _MimetypeResult:
    error = _exceptions.MimetypeDetectFailure( location = location )
    match behaviors.trial_decode:
        case _BehaviorTristate.Never: raise error
        case _: pass
    try:
        text, charset_result = _charsets.attempt_decodes(
            content,
            behaviors = behaviors, inference = charset, location = location )
    except _exceptions.ContentDecodeFailure: raise error from None
    match behaviors.text_validate:
        case _BehaviorTristate.Never: raise error
        case _: pass
    if not _validation.PROFILE_TEXTUAL( text ): raise error
    return _MimetypeResult(
        mimetype = 'text/plain', confidence = charset_result.confidence )


def _detect_via_chardet(
    content: _nomina.Content, behaviors: _Behaviors
) -> _CharsetResult | __.types.NotImplementedType:
    try: import chardet
    except ImportError: return NotImplemented
    result_ = chardet.detect( content )
    charset, confidence = result_[ 'encoding' ], result_[ 'confidence' ]
    return _CharsetResult( charset = charset, confidence = confidence )

charset_detectors[ 'chardet' ] = _detect_via_chardet


def _detect_via_charset_normalizer(
    content: _nomina.Content, behaviors: _Behaviors
) -> _CharsetResult | __.types.NotImplementedType:
    try: import charset_normalizer
    except ImportError: return NotImplemented
    result_ = charset_normalizer.from_bytes( content ).best( )
    charset = None if result_ is None else result_.encoding
    confidence = _core.confidence_from_bytes_quantity(
        content, behaviors = behaviors )
    return _CharsetResult( charset = charset, confidence = confidence )

charset_detectors[ 'charset-normalizer' ] = _detect_via_charset_normalizer


def _detect_via_magic(
    content: _nomina.Content, behaviors: _Behaviors
) -> _MimetypeResult | __.types.NotImplementedType:
    try: import magic
    except ImportError: return NotImplemented
    try: mimetype = magic.from_buffer( content, mime = True )
    except Exception: return NotImplemented
    confidence = _core.confidence_from_bytes_quantity(
        content, behaviors = behaviors )
    return _MimetypeResult( mimetype = mimetype, confidence = confidence )

mimetype_detectors[ 'magic' ] = _detect_via_magic


def _detect_via_puremagic(
    content: _nomina.Content, behaviors: _Behaviors
) -> _MimetypeResult | __.types.NotImplementedType:
    try: import puremagic
    except ImportError: return NotImplemented
    try: mimetype = puremagic.from_string( content, mime = True )
    except ( puremagic.PureError, ValueError ): return NotImplemented
    confidence = _core.confidence_from_bytes_quantity(
        content, behaviors = behaviors )
    return _MimetypeResult( mimetype = mimetype, confidence = confidence )

mimetype_detectors[ 'puremagic' ] = _detect_via_puremagic


def _normalize_charset_detection(
    content: _nomina.Content, behaviors: _Behaviors, result: _CharsetResult
) -> _CharsetResult:
    charset = result.charset
    if (    charset is not None
        and charset.lower( ) in ( 'utf-8-sig', 'utf_8_sig' )
        and not content.startswith( _BOM_BYTES )
    ): charset = 'utf-8'
    return _CharsetResult( charset = charset, confidence = result.confidence )
