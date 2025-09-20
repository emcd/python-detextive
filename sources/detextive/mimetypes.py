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


''' Determination of MIME types and textuality thereof. '''


from . import __
from . import nomina as _nomina


TEXTUAL_MIMETYPE_SUFFIXES = ( '+json', '+toml', '+xml', '+yaml' )
TEXTUAL_MIMETYPES = frozenset( (
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


def is_textual_mimetype( mimetype: str ) -> bool:
    ''' Checks if MIME type represents textual content. '''
    if mimetype.startswith( ( 'text/', 'text/x-' ) ): return True
    if mimetype in TEXTUAL_MIMETYPES: return True
    return mimetype.endswith( TEXTUAL_MIMETYPE_SUFFIXES )


def mimetype_from_location(
    location: _nomina.Location
) -> __.Absential[ str ]:
    ''' Determines MIME type from file location. '''
    # TODO: Python 3.13: Use __.mimetypes.guess_file_type for fs paths.
    mimetype, _ = __.mimetypes.guess_type( location )
    if mimetype: return mimetype
    return __.absent
