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
    CHARSET_DEFAULT as              _CHARSET_DEFAULT,
    MIMETYPE_DEFAULT as             _MIMETYPE_DEFAULT,
    BehaviorTristate as             _BehaviorTristate,
    Behaviors as                    _Behaviors,
    BehaviorsArgument as            _BehaviorsArgument,
    CharsetResult as                _CharsetResult,
    DetectFailureActions as         _DetectFailureActions,
    MimetypeResult as               _MimetypeResult,
)


CharsetDetector: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[
        [ _nomina.Content, _Behaviors ],
        _CharsetResult | __.types.NotImplementedType
    ],
    __.ddoc.Doc(
        ''' Character set detector function.

            Takes bytes content and behaviors object.

            Returns either a detection result or ``NotImplemented``. The
            detection result will include the name of the character set, which
            has been determined as able to decode the content, or ``None``, if
            it believes that no character set is applicable to the content, and
            the confidence of the detection.
        ''' ),
]
MimetypeDetector: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Callable[
        [ _nomina.Content, _Behaviors ],
        _MimetypeResult | __.types.NotImplementedType,
    ],
    __.ddoc.Doc(
        ''' MIME type detector function.

            Takes bytes content and behaviors object.

            Returns either a detection result or ``NotImplemented``. The
            detection result will include the MIME type and the confidence of
            the detection.
        ''' ),
]


charset_detectors: __.typx.Annotated[
    __.accret.Dictionary[ str, CharsetDetector ],
    __.ddoc.Doc( ''' Registry for character set detectors. ''' ),
] = __.accret.Dictionary( )
mimetype_detectors: __.typx.Annotated[
    __.accret.Dictionary[ str, MimetypeDetector ],
    __.ddoc.Doc( ''' Registry for MIME type detectors. ''' ),
] = __.accret.Dictionary( )


def detect_charset( # noqa: PLR0913
    content: _nomina.Content, /, *,
    behaviors: _BehaviorsArgument = _BEHAVIORS_DEFAULT,
    default: _nomina.CharsetDefaultArgument = _CHARSET_DEFAULT,
    supplement: _nomina.CharsetSupplementArgument = __.absent,
    mimetype: _nomina.MimetypeAssumptionArgument = __.absent,
    location: _nomina.LocationArgument = __.absent,
) -> __.typx.Optional[ str ]:
    ''' Detects character set. '''
    result = detect_charset_confidence(
        content,
        behaviors = behaviors,
        default = default,
        supplement = supplement,
        mimetype = mimetype,
        location = location )
    return result.charset


def detect_charset_confidence( # noqa: PLR0913
    content: _nomina.Content, /, *,
    behaviors: _BehaviorsArgument = _BEHAVIORS_DEFAULT,
    default: _nomina.CharsetDefaultArgument = _CHARSET_DEFAULT,
    supplement: _nomina.CharsetSupplementArgument = __.absent,
    mimetype: _nomina.MimetypeAssumptionArgument = __.absent,
    location: _nomina.LocationArgument = __.absent,
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
    else:
        match behaviors.charset_on_detect_failure:
            case _DetectFailureActions.Default:
                return _CharsetResult( charset = default, confidence = 0.0 )
            case _:
                raise _exceptions.CharsetDetectFailure( location = location )
    if result.charset is None:
        if __.is_absent( mimetype ): return result
        if not _mimetypes.is_textual_mimetype( mimetype ): return result
        result = _charsets.trial_decode_as_confident(
            content,
            behaviors = behaviors,
            supplement = supplement,
            location = location )
        return _normalize_charset_detection( content, behaviors, result )
    return _confirm_charset_detection(
        content, behaviors, result,
        supplement = supplement, location = location )


def detect_mimetype(
    content: _nomina.Content, /, *,
    behaviors: _BehaviorsArgument = _BEHAVIORS_DEFAULT,
    default: _nomina.MimetypeDefaultArgument = _MIMETYPE_DEFAULT,
    charset: _nomina.CharsetAssumptionArgument = __.absent,
    location: _nomina.LocationArgument = __.absent,
) -> str:
    ''' Detects most probable MIME type. '''
    nomargs: __.NominativeArguments = dict(
        behaviors = behaviors,
        default = default,
        charset = charset,
        location = location )
    result = detect_mimetype_confidence( content, **nomargs )
    return result.mimetype


def detect_mimetype_confidence(
    content: _nomina.Content, /, *,
    behaviors: _BehaviorsArgument = _BEHAVIORS_DEFAULT,
    default: _nomina.MimetypeDefaultArgument = _MIMETYPE_DEFAULT,
    charset: _nomina.CharsetAssumptionArgument = __.absent,
    location: _nomina.LocationArgument = __.absent,
) -> _MimetypeResult:
    ''' Detects MIME type candidates with confidence scores. '''
    if b'' == content:
        return _MimetypeResult( mimetype = 'text/plain', confidence = 1.0 )
    for name in behaviors.mimetype_detectors_order:
        detector = mimetype_detectors.get( name )
        if detector is None: continue
        result = detector( content, behaviors )
        if result is NotImplemented: continue
        return result
    if __.is_absent( charset ):
        match behaviors.mimetype_on_detect_failure:
            case _DetectFailureActions.Default:
                return _MimetypeResult( mimetype = default, confidence = 0.0 )
            case _:
                raise _exceptions.MimetypeDetectFailure( location = location )
    return _detect_mimetype_from_charset(
        content, behaviors, charset, default = default, location = location )


def _confirm_charset_detection( # noqa: PLR0911
    content: _nomina.Content,
    behaviors: _Behaviors,
    result: _CharsetResult, /, *,
    supplement: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> _CharsetResult:
    result = _normalize_charset_detection( content, behaviors, result )
    if result.charset is None: return result  # pragma: no cover
    charset, confidence = result.charset, result.confidence
    charset = behaviors.charset_promotions.get( charset, charset )
    if charset.startswith( 'utf-' ):
        result = _charsets.trial_decode_as_confident(
            content,
            behaviors = behaviors,
            supplement = supplement,
            inference = charset,
            confidence = confidence,
            location = location )
        return _normalize_charset_detection( content, behaviors, result )
    result = _CharsetResult( charset = charset, confidence = confidence )
    match behaviors.trial_decode:
        case _BehaviorTristate.Never: return result
        case _: # Shake out false positives, like 'MacRoman'.
            if charset == _charsets.discover_os_charset_default( ):
                # Allow 'windows-1252', etc..., as appropriate.
                return result  # pragma: no cover
            try:
                _, result_ = _charsets.attempt_decodes(
                    content,
                    behaviors = behaviors,
                    inference = 'utf-8-sig',
                    supplement = supplement,
                    location = location )
            except _exceptions.ContentDecodeFailure: return result
            if charset == result_.charset: return result  # pragma: no cover
            return _normalize_charset_detection( content, behaviors, result_ )


def _detect_mimetype_from_charset(
    content: _nomina.Content,
    behaviors: _Behaviors,
    charset: str, /, *,
    default: str,
    location: __.Absential[ _nomina.Location ],
) -> _MimetypeResult:
    should_error = False
    match behaviors.mimetype_on_detect_failure:
        case _DetectFailureActions.Default: pass
        case _: should_error = True
    error = _exceptions.MimetypeDetectFailure( location = location )
    result_default = _MimetypeResult( mimetype = default, confidence = 0.0 )
    match behaviors.trial_decode:
        case _BehaviorTristate.Never:
            if should_error: raise error
            return result_default
        case _: pass
    try:
        text, charset_result = _charsets.attempt_decodes(
            content,
            behaviors = behaviors, inference = charset, location = location )
    except _exceptions.ContentDecodeFailure:
        if should_error: raise error from None
        return result_default
    match behaviors.text_validate:
        case _BehaviorTristate.Never:
            if should_error: raise error
            return result_default
        case _: pass
    if not _validation.PROFILE_TEXTUAL( text ):
        if should_error: raise error
        return result_default
    return _MimetypeResult(
        mimetype = 'text/plain', confidence = charset_result.confidence )


def _detect_via_chardet(
    content: _nomina.Content, behaviors: _Behaviors
) -> _CharsetResult | __.types.NotImplementedType:
    try: import chardet  # pragma: no cover
    except ImportError: return NotImplemented  # pragma: no cover
    result_ = chardet.detect( content )
    charset, confidence = result_[ 'encoding' ], result_[ 'confidence' ]
    return _CharsetResult( charset = charset, confidence = confidence )

charset_detectors[ 'chardet' ] = _detect_via_chardet


def _detect_via_charset_normalizer(
    content: _nomina.Content, behaviors: _Behaviors
) -> _CharsetResult | __.types.NotImplementedType:
    try: import charset_normalizer  # pragma: no cover
    except ImportError: return NotImplemented  # pragma: no cover
    result_ = charset_normalizer.from_bytes( content ).best( )
    charset = None if result_ is None else result_.encoding  # pragma: no cover
    confidence = _core.confidence_from_bytes_quantity(
        content, behaviors = behaviors )
    return _CharsetResult( charset = charset, confidence = confidence )

charset_detectors[ 'charset-normalizer' ] = _detect_via_charset_normalizer


def _detect_via_magic(
    content: _nomina.Content, behaviors: _Behaviors
) -> _MimetypeResult | __.types.NotImplementedType:
    try: import magic  # pragma: no cover
    except ImportError: return NotImplemented  # pragma: no cover
    try: mimetype = magic.from_buffer( content, mime = True )
    except Exception: return NotImplemented  # pragma: no cover
    confidence = _core.confidence_from_bytes_quantity(
        content, behaviors = behaviors )
    return _MimetypeResult( mimetype = mimetype, confidence = confidence )

mimetype_detectors[ 'magic' ] = _detect_via_magic


def _detect_via_puremagic(
    content: _nomina.Content, behaviors: _Behaviors
) -> _MimetypeResult | __.types.NotImplementedType:
    try: import puremagic  # pragma: no cover
    except ImportError: return NotImplemented  # pragma: no cover
    try: mimetype = puremagic.from_string( content, mime = True )
    except ( puremagic.PureError, ValueError ):  # pragma: no cover
        return NotImplemented
    confidence = _core.confidence_from_bytes_quantity(
        content, behaviors = behaviors )
    return _MimetypeResult( mimetype = mimetype, confidence = confidence )

mimetype_detectors[ 'puremagic' ] = _detect_via_puremagic


def _normalize_charset_detection(
    content: _nomina.Content, behaviors: _Behaviors, result: _CharsetResult
) -> _CharsetResult:
    if result.charset is None: return result  # pragma: no cover
    charset = _charsets.normalize_charset( result.charset )
    # TODO? Consider endianness variations for BOM.
    if charset == 'utf-8-sig' and not content.startswith( __.codecs.BOM ):
        charset = 'utf-8'
    return _CharsetResult( charset = charset, confidence = result.confidence )
