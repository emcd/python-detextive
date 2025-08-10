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
from .exceptions import TextualMimetypeInvalidity


# Type aliases with documentation
Content: __.typx.TypeAlias = __.typx.Annotated[
    bytes, 
    __.ddoc.Doc( "Raw byte content for analysis." )
]

Location: __.typx.TypeAlias = __.typx.Annotated[
    __.typx.Union[ str, __.Path, __.cabc.Sequence[ str ] ],
    __.ddoc.Doc( "File path, URL, or path components for context." )
]

# Textual MIME type patterns consolidated from all sources
_TEXTUAL_MIME_TYPES = frozenset( (
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

_TEXTUAL_SUFFIXES = ( '+xml', '+json', '+yaml', '+toml' )


def detect_charset( content: Content ) -> __.typx.Optional[ str ]:
    ''' Detects character encoding with UTF-8 preference and validation.
    
        Applies statistical analysis using chardet library with UTF-8 bias.
        Validates detected encodings through trial decoding to eliminate
        false positives like 'MacRoman'. Returns encoding names compatible 
        with Python's codec system.
        
        Returns None if no reliable encoding can be determined.
    '''
    result = __.chardet.detect( content )
    charset = result[ 'encoding' ]
    if charset is None: return charset
    if charset.startswith( 'utf' ): return charset
    match charset:
        case 'ascii': return 'utf-8'  # Assume superset
        case _: pass
    # Shake out false positives, like 'MacRoman'
    try: content.decode( 'utf-8' )
    except UnicodeDecodeError: return charset
    return 'utf-8'


def detect_mimetype(
    content: Content,
    location: Location
) -> __.typx.Optional[ str ]:
    ''' Detects MIME type using content analysis and extension fallback.
        
        Returns standardized MIME type strings or None if detection fails.
    '''
    try: return __.puremagic.from_string( content, mime = True )
    except ( __.puremagic.PureError, ValueError ):
        return __.mimetypes.guess_type( str( location ) )[ 0 ]


def detect_mimetype_and_charset(
    content: Content,
    location: Location, *,
    mimetype: __.Absential[ str ] = __.absent,
    charset: __.Absential[ str ] = __.absent,
) -> tuple[ str, __.typx.Optional[ str ] ]:
    ''' Detects MIME type and charset with optional parameter overrides.
        
        Returns tuple of (mimetype, charset). MIME type defaults to 
        'text/plain' if charset detected but MIME type unknown, or 
        'application/octet-stream' if neither detected.
    '''
    if __.is_absent( mimetype ):
        mimetype_ = detect_mimetype( content, location )
    else: mimetype_ = mimetype
    if __.is_absent( charset ):  # noqa: SIM108
        charset_ = detect_charset( content )
    else: charset_ = charset
    if not mimetype_:
        if charset_:
            mimetype_ = 'text/plain'
            _validate_mimetype_with_trial_decode(
                content, str( location ), mimetype_, charset_ )
            return mimetype_, charset_
        mimetype_ = 'application/octet-stream'
    if is_textual_mimetype( mimetype_ ):
        return mimetype_, charset_
    if charset_ is None:
        raise TextualMimetypeInvalidity( str( location ), mimetype_ )
    _validate_mimetype_with_trial_decode(
        content, str( location ), mimetype_, charset_ )
    return mimetype_, charset_


def is_textual_mimetype( mimetype: str ) -> bool:
    ''' Validates if MIME type represents textual content.
    
        Consolidates textual MIME type patterns from all source 
        implementations. Supports text/* prefix, specific application
        types (JSON, XML, JavaScript, etc.), and textual suffixes
        (+xml, +json, +yaml, +toml).
        
        Returns True for MIME types representing textual content.
    '''
    if mimetype.startswith( ( 'text/', 'text/x-' ) ): return True
    if mimetype in _TEXTUAL_MIME_TYPES: return True
    return mimetype.endswith( _TEXTUAL_SUFFIXES )


def is_reasonable_text_content( content: str ) -> bool:
    ''' Validates decoded content using heuristic analysis.
    
        Applies heuristics to detect meaningful text vs binary data:
        - Rejects empty content and single-character repetition
        - Limits control characters to <10% (excluding common whitespace)
        - Requires >=80% printable characters
        
        Returns True for content likely to be meaningful text.
    '''
    if not content: return False
    # Check for excessive repetition of single characters (likely binary)
    if len( set( content ) ) == 1: return False
    # Check for excessive control characters (excluding common whitespace)
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


def _validate_mimetype_with_trial_decode(
    content: bytes, 
    location: __.typx.Union[ str, __.Path ],
    mimetype: str, 
    charset: str
) -> None:
    ''' Validates charset fallback and returns appropriate MIME type. '''
    try: text = content.decode( charset )
    except ( UnicodeDecodeError, LookupError ) as exc:
        raise TextualMimetypeInvalidity( str( location ), mimetype ) from exc
    if not is_reasonable_text_content( text ):
        raise TextualMimetypeInvalidity( str( location ), mimetype )