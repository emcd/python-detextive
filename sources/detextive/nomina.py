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


''' Common names and type aliases. '''


from . import __


Content: __.typx.TypeAlias = __.typx.Annotated[
    bytes,
    __.ddoc.Doc( ''' Raw byte content for analysis. ''' ),
]
Location: __.typx.TypeAlias = __.typx.Annotated[
    str | __.os.PathLike[ str ],
    __.ddoc.Doc( ''' Local filesystem location or URL for context. ''' ),
]

CharsetAssumptionArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ str ],
    __.ddoc.Doc(
        ''' Character set hint to influence MIME type detection. ''' ),
]
CharsetDefaultArgument: __.typx.TypeAlias = __.typx.Annotated[
    str,
    __.ddoc.Doc(
        ''' Fallback character set returned on inference/detection failure.
        ''' ),
]
CharsetSupplementArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ str ],
    __.ddoc.Doc(
        ''' User-supplied character set hint for trial decode attempts. ''' ),
]
HttpContentTypeArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ str ],
    __.ddoc.Doc( ''' HTTP Content-Type header for parsing context. ''' ),
]
LocationArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ Location ],
    __.ddoc.Doc( ''' File location or URL for error reporting context. ''' ),
]
MimetypeAssumptionArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ str ],
    __.ddoc.Doc(
        ''' MIME type hint to influence character set detection. ''' ),
]
MimetypeDefaultArgument: __.typx.TypeAlias = __.typx.Annotated[
    str,
    __.ddoc.Doc(
        ''' Fallback MIME type returned on inference/detection failure. ''' ),
]
MimetypeSupplementArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ str ],
    __.ddoc.Doc( ''' User-supplied MIME type hint for inference. ''' ),
]
