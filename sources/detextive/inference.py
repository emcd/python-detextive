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
from . import exceptions as _exceptions
from . import nomina as _nomina

from .interfaces import (
    BehaviorTristate as             _BehaviorTristate,
    Behaviors as                    _Behaviors,
    CodecSpecifiers as              _CodecSpecifiers,
)


_TEXTUAL_MIMETYPE_SUFFIXES = ( '+json', '+toml', '+xml', '+yaml' )
_TEXTUAL_MIMETYPES = frozenset( (
    'application/ecmascript',
    'application/graphql',
    'application/javascript',
    'application/json',
    'application/ld+json',
    'application/x-httpd-php',
    'application/x-javascript',
    'application/x-latex',
    'application/x-perl',
    'application/x-php',
    'application/x-python',
    'application/x-ruby',
    'application/x-shell',
    'application/x-tex',
    'application/x-yaml',
    'application/xhtml+xml',
    'application/xml',
    'application/yaml',
    'image/svg+xml',
) )


behaviors_default = _Behaviors( )


# TODO: Implement 'decode' function. Returns text from bytes.
#       Sets charset trial decodes to Never, since real decode happens.


def detect_charset(
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = behaviors_default,
    default: __.Absential[ str ] = __.absent,
    mimetype: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> __.typx.Optional[ str ]:
    ''' Detects character set. '''
    charset = _detect_charset(
        content, behaviors,
        default = default, location = location, mimetype = mimetype )
    has_textual_mimetype = (
        __.is_absent( mimetype ) or is_textual_mimetype( mimetype ) )
    if has_textual_mimetype and charset is not None:
        # TODO: Call 'validate_text' with 'TEXTUAL' validation profile.
        pass
    return charset


def detect_mimetype(
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = behaviors_default,
    charset: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> str:
    ''' Detects MIME type. '''
    mimetype = _detect_mimetype(
        content, behaviors, charset = charset, location = location )
    if not __.is_absent( charset ) and is_textual_mimetype( mimetype ):
        # TODO: Call 'validate_text' with 'TEXTUAL' validation profile.
        pass
    return mimetype


def infer_charset(
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = behaviors_default,
    http_content_type: __.Absential[ str ] = __.absent,
    default: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> __.typx.Optional[ str ]:
    ''' Infers charset through various means. '''
    should_parse, should_detect = (
        _determine_parse_detect( behaviors.charset_detect ) )
    charset = __.absent
    mimetype = __.absent
    http_content_type = (
        '' if __.is_absent( http_content_type ) else http_content_type )
    posargs: __.PositionalArguments = ( content, behaviors )
    if should_parse and http_content_type:
        mimetype, charset = parse_http_content_type( http_content_type )
        nomargs: __.NominativeArguments = dict(
            charset_default = default,
            charset_inference = charset,
            location = location )
        charset = _trial_decode_as_mandatory( *posargs, **nomargs )
    if __.is_absent( charset ) and should_detect:
        charset = _detect_charset( *posargs, mimetype = mimetype )
    if __.is_absent( charset ):
        raise _exceptions.CharsetInferFailure( location = location )
    has_textual_mimetype = (
        __.is_absent( mimetype ) or is_textual_mimetype( mimetype ) )
    if has_textual_mimetype and charset is not None:
        # TODO: Call 'validate_text' with 'TEXTUAL' validation profile.
        pass
    return charset


def infer_mimetype_charset( # noqa: PLR0913
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = behaviors_default,
    http_content_type: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
    charset_default: __.Absential[ str ] = __.absent,
    mimetype_default: __.Absential[ str ] = __.absent,
) -> tuple[ str, __.typx.Optional[ str ] ]:
    ''' Infers MIME type and charset through various means. '''
    should_parse, should_detect_charset = (
        _determine_parse_detect( behaviors.charset_detect ) )
    should_parse, should_detect_mimetype = (
        _determine_parse_detect(
            behaviors.mimetype_detect, should_parse = should_parse ) )
    charset = __.absent
    mimetype = __.absent
    http_content_type = (
        '' if __.is_absent( http_content_type ) else http_content_type )
    posargs: __.PositionalArguments = ( content, behaviors )
    if should_parse:
        if http_content_type:
            mimetype, charset = parse_http_content_type( http_content_type )
        nomargs: __.NominativeArguments = dict(
            charset_default = charset_default,
            charset_inference = charset,
            location = location )
        charset = _trial_decode_as_mandatory( *posargs, **nomargs )
        if __.is_absent( mimetype ) and not __.is_absent( location ):
            mimetype = mimetype_from_location( location )
    if __.is_absent( mimetype ) and should_detect_mimetype:
        nomargs: __.NominativeArguments = dict( location = location )
        if not __.is_absent( charset ): nomargs[ 'charset' ] = charset
        mimetype = _detect_mimetype( *posargs, **nomargs )
    if __.is_absent( charset ) and should_detect_charset:
        nomargs: __.NominativeArguments = dict( location = location )
        if not __.is_absent( mimetype ): nomargs[ 'mimetype' ] = mimetype
        charset = _detect_charset( *posargs, **nomargs )
    if __.is_absent( charset ):
        raise _exceptions.CharsetInferFailure( location = location )
    if __.is_absent( mimetype ):
        raise _exceptions.MimetypeInferFailure( location = location )
    if is_textual_mimetype( mimetype ) and charset is not None:
        # TODO: Call 'validate_text' with 'TEXTUAL' validation profile.
        pass
    return mimetype, charset


# def is_textual_content( content: bytes ) -> bool:
#     ''' Determines if byte content represents textual data.
#
#         Returns True for content that can be reliably processed as text.
#     '''
#     mimetype, charset = detect_mimetype_and_charset( content, 'unknown' )
#     return charset is not None and is_textual_mimetype( mimetype )


def is_textual_mimetype( mimetype: str ) -> bool:
    ''' Checks if MIME type represents textual content. '''
    if mimetype.startswith( ( 'text/', 'text/x-' ) ): return True
    if mimetype in _TEXTUAL_MIMETYPES: return True
    return mimetype.endswith( _TEXTUAL_MIMETYPE_SUFFIXES )


def is_valid_text(
    text: str,
    # TODO: text validation profile DTO
) -> bool:
    ''' Is text valid? '''
    # TODO: Check according to profile.
    #       (TEXTUAL, TERMINAL_SAFE, TERMINAL_SAFE_NOANSI, PRINTER_SAFE)
    #       Or custom profile.
    #       TEXTUAL should exclude C0 and C1, minus whitespace.
    #       Consider BIDI markers.
    #       Consider Unicode categories.
    if not text: return False
    # TODO: Implement.
    return False


def mimetype_from_location(
    location: _nomina.Location
) -> __.Absential[ str ]:
    ''' Determines MIME type from file location. '''
    # TODO: Python 3.13: Use __.mimetypes.guess_file_type for fs paths.
    mimetype, _ = __.mimetypes.guess_type( location )
    if mimetype: return mimetype
    return __.absent


def parse_http_content_type(
    http_content_type: str
) -> tuple[ __.Absential[ str ], __.Absential[ __.typx.Optional[ str ] ] ]:
    ''' Parses RFC 9110 HTTP Content-Type header.

        Returns normalized MIME type and charset, if able to be extracted.
        Marks either as absent, if not able to be extracted.
    '''
    mimetype, *params = http_content_type.split( ';' )
    if mimetype:
        mimetype = mimetype.strip( ).lower( )
        if is_textual_mimetype( mimetype ):
            for param in params:
                name, value = param.split( '=' )
                if 'charset' == name.strip( ).lower( ):
                    return mimetype, value.strip( ).lower( )
            return mimetype, __.absent
        return mimetype, None  # non-textual type, charset irrelevant
    return __.absent, __.absent


def _detect_charset( # noqa: PLR0911
    content: _nomina.Content,
    behaviors: _Behaviors, /, *,
    default: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
    mimetype: __.Absential[ str ] = __.absent,
) -> __.typx.Optional[ str ]:
    # TODO: Use 'charset-normalizer', if available.
    # TODO? Return confidence from detector.
    ''' Detects character set. '''
    result = __.chardet.detect( content )
    charset = result[ 'encoding' ]
    nomargs: __.NominativeArguments = dict(
        charset_default = default, location = location )
    posargs: __.PositionalArguments = ( content, behaviors )
    if charset is None:
        if __.is_absent( mimetype ): return None
        if is_textual_mimetype( mimetype ):
            charset = _trial_decode_as_necessary( *posargs, **nomargs )
            if __.is_absent( charset ): return None
            return charset
        return None
    charset = behaviors.charset_promotions.get( charset, charset )
    nomargs_: __.NominativeArguments = dict(
        charset_inference = charset, **nomargs )
    if charset.startswith( 'utf-' ):
        charset = _trial_decode_as_mandatory( *posargs, **nomargs_ )
        return __.typx.cast( str, charset )
    match behaviors.charset_trial_decode:
        case _BehaviorTristate.Never: return charset
        # Shake out false positives, like 'MacRoman'.
        case _:
            if charset == __.locale.getpreferredencoding( ):
                # Allow 'windows-1252', etc..., as appropriate.
                return charset
            charset_ = _trial_decode( *posargs, **nomargs )
            if __.is_absent( charset_ ): return charset
            return charset_


def _detect_mimetype(
    content: _nomina.Content,
    behaviors: _Behaviors, /, *,
    charset: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> str:
    # TODO: Use 'magic', if available.
    # TODO? Return confidence, based on content length.
    ''' Detects MIME type. '''
    posargs: __.PositionalArguments = ( content, behaviors )
    try: return __.puremagic.from_string( content, mime = True )
    except ( __.puremagic.PureError, ValueError ) as exc_magic:
        Error = _exceptions.MimetypeDetectFailure
        # If content is textual, then we can at least return 'text/plain'.
        if not __.is_absent( charset ):
            nomargs: __.NominativeArguments = dict(
                charset_inference = charset, location = location )
            try: charset_ = _trial_decode_as_necessary( *posargs, **nomargs )
            except _exceptions.ContentDecodeFailure:
                raise Error( location = location ) from None
            if not __.is_absent( charset_ ): return 'text/plain'
        raise Error( location = location ) from exc_magic


def _determine_parse_detect(
    detect_tristate: _BehaviorTristate, should_parse = False
) -> tuple[ bool, bool ]:
    match detect_tristate:
        case _BehaviorTristate.Always:
            should_parse = should_parse or False
            should_detect = True
        case _BehaviorTristate.AsNeeded:
            should_parse = should_parse or True
            should_detect = True
        case _BehaviorTristate.Never:
            should_parse = should_parse or True
            should_detect = False
    return should_parse, should_detect


def _is_probable_textual_content( content: str ) -> bool:
    ''' Validates decoded content using heuristic analysis.

        Applies heuristics to detect meaningful text vs binary data:
        - Limits control characters to <10% (excluding common whitespace)
        - Requires >=80% printable characters

        Returns True for content likely to be meaningful text.
    '''
    if not content: return False
    common_whitespace = '\t\n\r'
    ascii_control_limit = 32
    control_chars = sum(
        1 for c in content
        if ord( c ) < ascii_control_limit and c not in common_whitespace )
    if control_chars > len( content ) * 0.1: return False
    printable_chars = sum(
        1 for c in content
        if c.isprintable( ) or c in common_whitespace )
    return printable_chars >= len( content ) * 0.8


def _trial_decode(
    content: _nomina.Content,
    behaviors: _Behaviors, /, *,
    charset_inference: __.Absential[ str ] = __.absent,
    charset_default: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> str:
    trials: list[ str ] = [ ]
    for codec in behaviors.charset_trial_codecs:
        match codec:
            # TODO? Python default (different than OS default)
            case _CodecSpecifiers.Inference:
                if __.is_absent( charset_inference ): continue
                charset = charset_inference
            case _CodecSpecifiers.OsDefault:
                charset = __.locale.getpreferredencoding( )
            case _CodecSpecifiers.UserDefault:
                if __.is_absent( charset_default ): continue
                charset = charset_default
            case _: pass
        try: content.decode( charset )
        except UnicodeDecodeError:
            trials.append( charset )
            continue
        return charset
    raise _exceptions.ContentDecodeFailure(
        charset = trials, location = location )


def _trial_decode_as_mandatory(
    content: _nomina.Content,
    behaviors: _Behaviors, /, *,
    charset_inference: __.Absential[ __.typx.Optional[ str ] ] = __.absent,
    charset_default: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> __.Absential[ __.typx.Optional[ str ] ]:
    nomargs: __.NominativeArguments = dict(
        charset_default = charset_default, location = location )
    posargs: __.PositionalArguments = ( content, behaviors )
    if charset_inference is not None:
        nomargs[ 'charset_inference' ] = charset_inference
    match behaviors.charset_trial_decode:
        case _BehaviorTristate.Always:
            return _trial_decode( *posargs, **nomargs )
        case _: return charset_inference


def _trial_decode_as_necessary(
    content: _nomina.Content,
    behaviors: _Behaviors, /, *,
    charset_inference: __.Absential[ __.typx.Optional[ str ] ] = __.absent,
    charset_default: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> __.Absential[ __.typx.Optional[ str ] ]:
    nomargs: __.NominativeArguments = dict(
        charset_default = charset_default, location = location )
    posargs: __.PositionalArguments = ( content, behaviors )
    if charset_inference is not None:
        nomargs[ 'charset_inference' ] = charset_inference
    match behaviors.charset_trial_decode:
        case _BehaviorTristate.Never: return charset_inference
        case _: return _trial_decode( *posargs, **nomargs )
