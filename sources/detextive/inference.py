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

from .behaviors import ( # isort: skip
    BEHAVIORS_DEFAULT as    _BEHAVIORS_DEFAULT,
    BehaviorTristate as     _BehaviorTristate,
    Behaviors as            _Behaviors,
)


def infer_charset(
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = _BEHAVIORS_DEFAULT,
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
    if should_parse and http_content_type:
        mimetype, charset = parse_http_content_type( http_content_type )
        nomargs: __.NominativeArguments = dict(
            behaviors = behaviors,
            charset_default = default,
            charset_inference = charset,
            location = location )
        charset = _charsets.trial_decode_as_mandatory( content, **nomargs )
    if __.is_absent( charset ) and should_detect:
        charset = _detectors.detect_charset( content, mimetype = mimetype )
    if __.is_absent( charset ):
        raise _exceptions.CharsetInferFailure( location = location )
    return charset


def infer_mimetype_charset( # noqa: PLR0913
    content: _nomina.Content, /, *,
    behaviors: _Behaviors = _BEHAVIORS_DEFAULT,
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
    nomargs: __.NominativeArguments = dict(
        behaviors = behaviors, location = location )
    charset = __.absent
    mimetype = __.absent
    http_content_type = (
        '' if __.is_absent( http_content_type ) else http_content_type )
    if should_parse:
        if http_content_type:
            mimetype, charset = parse_http_content_type( http_content_type )
        nomargs_: __.NominativeArguments = dict(
            charset_default = charset_default,
            charset_inference = charset,
            **nomargs )
        charset = _charsets.trial_decode_as_mandatory( content, **nomargs_ )
        if __.is_absent( mimetype ) and not __.is_absent( location ):
            mimetype = _mimetypes.mimetype_from_location( location )
    if __.is_absent( mimetype ) and should_detect_mimetype:
        nomargs_: __.NominativeArguments = dict( **nomargs )
        if not __.is_absent( charset ): nomargs_[ 'charset' ] = charset
        mimetype = _detectors.detect_mimetype( content, **nomargs_ )
    if __.is_absent( charset ) and should_detect_charset:
        nomargs_: __.NominativeArguments = dict( **nomargs )
        if not __.is_absent( mimetype ): nomargs_[ 'mimetype' ] = mimetype
        charset = _detectors.detect_charset( content, **nomargs_ )
    if __.is_absent( charset ):
        raise _exceptions.CharsetInferFailure( location = location )
    if __.is_absent( mimetype ):
        raise _exceptions.MimetypeInferFailure( location = location )
    return mimetype, charset


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
