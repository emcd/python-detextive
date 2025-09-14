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
from . import detectors as _detectors
from . import exceptions as _exceptions
from . import mimetypes as _mimetypes
from . import nomina as _nomina

from .core import ( # isort: skip
    BEHAVIORS_DEFAULT as    _BEHAVIORS_DEFAULT,
    BehaviorTristate as     _BehaviorTristate,
    Behaviors as            _Behaviors,
    Result as               _Result,
)


def infer_charset( # noqa: PLR0913
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = _BEHAVIORS_DEFAULT,
    http_content_type: __.Absential[ str ] = __.absent,
    charset_supplement: __.Absential[ str ] = __.absent,
    mimetype_supplement: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> __.typx.Optional[ str ]:
    ''' Infers charset through various means. '''
    result = infer_charset_confidence(
        content,
        behaviors = behaviors,
        http_content_type = http_content_type,
        charset_supplement = charset_supplement,
        mimetype_supplement = mimetype_supplement,
        location = location )
    if result is None: return None
    return result.value


def infer_charset_confidence( # noqa: PLR0913
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = _BEHAVIORS_DEFAULT,
    http_content_type: __.Absential[ str ] = __.absent,
    charset_supplement: __.Absential[ str ] = __.absent,
    mimetype_supplement: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> __.typx.Optional[ _Result ]:
    ''' Infers charset with confidence level through various means. '''
    if content == b'': return _Result( value = 'utf-8', confidence = 1.0 )
    should_parse, should_detect = (
        _determine_parse_detect( behaviors.charset_detect ) )
    result = __.absent
    mimetype = mimetype_supplement
    http_content_type = (
        '' if __.is_absent( http_content_type ) else http_content_type )
    if should_parse and http_content_type:
        mimetype_result, charset_result = _validate_http_content_type(
            content, behaviors, http_content_type,
            charset_supplement = charset_supplement, location = location )
        if not __.is_absent( mimetype_result ):
            mimetype = mimetype_result.value
        if charset_result is not None and not __.is_absent( charset_result ):
            return charset_result
    if __.is_absent( result ) and should_detect:
        result = _detectors.detect_charset_confidence(
            content, mimetype = mimetype )
    if __.is_absent( result ):
        raise _exceptions.CharsetInferFailure( location = location )
    return result


def infer_mimetype_charset( # noqa: PLR0913
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = _BEHAVIORS_DEFAULT,
    http_content_type: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
    charset_supplement: __.Absential[ str ] = __.absent,
    mimetype_supplement: __.Absential[ str ] = __.absent,
) -> tuple[ str, __.typx.Optional[ str ] ]:
    ''' Infers MIME type and charset through various means. '''
    mimetype_result, charset_result = (
        infer_mimetype_charset_confidence(
            content,
            behaviors = behaviors,
            http_content_type = http_content_type,
            location = location,
            charset_supplement = charset_supplement,
            mimetype_supplement = mimetype_supplement ) )
    if charset_result is None:
        return mimetype_result.value, None
    return mimetype_result.value, charset_result.value


def infer_mimetype_charset_confidence( # noqa: PLR0913
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = _BEHAVIORS_DEFAULT,
    http_content_type: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
    charset_supplement: __.Absential[ str ] = __.absent,
    mimetype_supplement: __.Absential[ str ] = __.absent,
) -> tuple[ _Result, __.typx.Optional[ _Result ] ]:
    ''' Infers MIME type and charset through various means. '''
    should_parse, should_detect_charset = (
        _determine_parse_detect( behaviors.charset_detect ) )
    should_parse, should_detect_mimetype = (
        _determine_parse_detect(
            behaviors.mimetype_detect, should_parse = should_parse ) )
    nomargs: __.NominativeArguments = dict(
        behaviors = behaviors, location = location )
    charset_result: __.Absential[ __.typx.Optional[ _Result ] ] = __.absent
    mimetype_result: __.Absential[ _Result ] = __.absent
    http_content_type = (
        '' if __.is_absent( http_content_type ) else http_content_type )
    if should_parse:
        if http_content_type:
            mimetype_result, charset_result = _validate_http_content_type(
                content, behaviors, http_content_type,
                charset_supplement = charset_supplement, location = location )
        if __.is_absent( mimetype_result ) and not __.is_absent( location ):
            mimetype = _mimetypes.mimetype_from_location( location )
            if not __.is_absent( mimetype ):
                mimetype_result = _Result( value = mimetype, confidence = 0.9 )
    if __.is_absent( mimetype_result ) and should_detect_mimetype:
        charset = (
            charset_supplement
            if charset_result is None or __.is_absent( charset_result )
            else charset_result.value )
        nomargs_: __.NominativeArguments = dict(
            charset = charset, **nomargs )
        mimetype_result = (
            _detectors.detect_mimetype_confidence( content, **nomargs_ ) )
    if __.is_absent( charset_result ) and should_detect_charset:
        mimetype = (
            mimetype_supplement if __.is_absent( mimetype_result )
            else mimetype_result.value )
        nomargs_: __.NominativeArguments = dict(
            mimetype = mimetype, **nomargs )
        charset_result = (
            _detectors.detect_charset_confidence( content, **nomargs_ ) )
    if __.is_absent( charset_result ):
        raise _exceptions.CharsetInferFailure( location = location )
    if __.is_absent( mimetype_result ):
        raise _exceptions.MimetypeInferFailure( location = location )
    return mimetype_result, charset_result


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
        if _mimetypes.is_textual_mimetype( mimetype ):
            for param in params:
                name, value = param.split( '=' )
                if 'charset' == name.strip( ).lower( ):
                    return mimetype, value.strip( ).lower( )
            return mimetype, __.absent
        return mimetype, None  # non-textual type, charset irrelevant
    return __.absent, __.absent


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


def _validate_http_content_type(
    content: _nomina.Content,
    behaviors: _Behaviors,
    http_content_type: str, /, *,
    charset_supplement: __.Absential[ str ] = __.absent,
    location: __.Absential[ _nomina.Location ] = __.absent,
) -> tuple[
    __.Absential[ _Result ],
    __.Absential[ __.typx.Optional[ _Result ] ]
]:
    mimetype, charset = parse_http_content_type( http_content_type )
    if __.is_absent( charset ): charset_result = __.absent
    elif charset is None: charset_result = None
    else:
        nomargs: __.NominativeArguments = dict(
            behaviors = behaviors,
            inference = charset,
            supplement = charset_supplement )
        charset_result = (
            _charsets.trial_decode_as_confident( content, **nomargs ) )
    if __.is_absent( mimetype ): mimetype_result = __.absent
    else: mimetype_result = _Result( value = mimetype, confidence = 0.9 )
    return mimetype_result, charset_result
