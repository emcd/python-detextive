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


''' Validation of textual content. '''


from . import __


_HYPERCATEGORIES_PRINTABLE = frozenset( ( 'L', 'M', 'N', 'P', 'S', 'Z' ) )

BELL_CHARACTER = '\x07'         # BEL
BOM_CHARACTER = '\ufeff'        # UTF Byte-Ordering Mark
DELETE_CHARACTER = '\x7F'       # DEL
ESCAPE_CHARACTER = '\x1B'       # ESC
FORMFEED_CHARACTER = '\x0C'     # FF

BIDI_ISOLATE_CHARACTERS = frozenset( (
    # Bidi isolates (Unicode 6.3, recommended)
    '\u2066',  # LEFT-TO-RIGHT ISOLATE (LRI)
    '\u2067',  # RIGHT-TO-LEFT ISOLATE (RLI)
    '\u2068',  # FIRST STRONG ISOLATE (FSI)
    '\u2069',  # POP DIRECTIONAL ISOLATE (PDI)
) )
BIDI_LEGACY_CHARACTERS = frozenset( (
    # Legacy bidi controls (Unicode 3.0, deprecated but still used)
    '\u202A',  # LEFT-TO-RIGHT EMBEDDING (LRE)
    '\u202B',  # RIGHT-TO-LEFT EMBEDDING (RLE)
    '\u202C',  # POP DIRECTIONAL FORMATTING (PDF)
    '\u202D',  # LEFT-TO-RIGHT OVERRIDE (LRO)
    '\u202E',  # RIGHT-TO-LEFT OVERRIDE (RLO)
) )
C0_WHITESPACE_CHARACTERS = frozenset( ( '\t', '\n', '\r' ) )
DIRECTIONAL_MARK_CHARACTERS = frozenset( (
    '\u061C',  # ARABIC LETTER MARK
    '\u200E',  # LEFT-TO-RIGHT MARK (LRM)
    '\u200F',  # RIGHT-TO-LEFT MARK (RLM)
) )
ZERO_WIDTH_CHARACTERS = frozenset( (
    '\u200C',  # ZERO WIDTH NON-JOINER (ZWNJ)
    '\u200D',  # ZERO WIDTH JOINER (ZWJ)
) )

CONTROL_CHARACTERS_TEXTUAL = (
        BIDI_ISOLATE_CHARACTERS
    |   BIDI_LEGACY_CHARACTERS
    |   C0_WHITESPACE_CHARACTERS
    |   DIRECTIONAL_MARK_CHARACTERS
    |   ZERO_WIDTH_CHARACTERS )


class TextValidationProfile( __.immut.Dataclass ):
    ''' Configuration for text validation heuristics. '''

    acceptable_characters: __.typx.Annotated[
        __.cabc.Set[ str ],
        __.ddoc.Doc(
            ''' Set of characters which are always considered valid. ''' ),
    ] = CONTROL_CHARACTERS_TEXTUAL
    check_bom: __.typx.Annotated[
        bool,
        __.ddoc.Doc( ''' Allow leading BOM; reject embedded BOMs. ''' ),
    ] = True
    printables_ratio_min: __.typx.Annotated[
        float,
        __.ddoc.Doc(
            ''' Minimum ratio of printable characters to total characters.
            ''' ),
    ] = 0.85
    rejectable_characters: __.typx.Annotated[
        __.cabc.Set[ str ],
        __.ddoc.Doc(
            ''' Set of characters which are always considered invalid. ''' ),
    ] = frozenset( ( DELETE_CHARACTER, ) )
    rejectable_families: __.typx.Annotated[
        __.cabc.Set[ str ],
        __.ddoc.Doc(
            ''' Set of Unicode categories which are always considered invalid.
            ''' ),
    ] = frozenset( ( 'Cc', 'Cf', 'Cs', 'Co' ) )
    rejectables_ratio_max: __.typx.Annotated[
        float,
        __.ddoc.Doc(
            ''' Maximum ratio of rejectable characters to total characters.
            ''' ),
    ] = 0.0
    sample_quantity: __.typx.Annotated[
        __.typx.Optional[ int ],
        __.ddoc.Doc( ''' Number of characters to sample. ''' ),
    ] = 8192
    # TODO: check_bidi_safety: validate bidirectional text safety
    # TODO: normalize_unicode: apply NFC normalization before validation
    # TODO: permit_ansi_sequences: allow ANSI SGR and other C0/C1 sequences?

    def __call__( self, text: str ) -> bool:
        ''' Is text valid against this profile? '''
        return is_valid_text( text, profile = self )


PROFILE_PRINTER = TextValidationProfile(
    acceptable_characters = (
        CONTROL_CHARACTERS_TEXTUAL | { FORMFEED_CHARACTER } ),
    check_bom = False,
    rejectable_families = frozenset( ( 'Cc', 'Cf', 'Cs', 'Co', 'Zl', 'Zp' ) ) )

PROFILE_TEXTUAL = TextValidationProfile( )

PROFILE_TERMINAL = TextValidationProfile(
    check_bom = False,
    rejectable_families = frozenset( ( 'Cc', 'Cf', 'Cs', 'Co', 'Zl', 'Zp' ) ) )

PROFILE_TERMINAL_ANSI = TextValidationProfile(
    acceptable_characters = (
        CONTROL_CHARACTERS_TEXTUAL | { ESCAPE_CHARACTER } ),
    check_bom = False,
    rejectable_families = frozenset( ( 'Cc', 'Cf', 'Cs', 'Co', 'Zl', 'Zp' ) ) )


def is_valid_text(
    text: str, /, profile: TextValidationProfile = PROFILE_TEXTUAL
) -> bool:
    ''' Is content valid against profile? '''
    if not text: return False
    index_i = 1 if profile.check_bom and text[ 0 ] == BOM_CHARACTER else 0
    index_f = len( text )
    if profile.sample_quantity is not None:
        index_f = min( profile.sample_quantity, index_f )
    sample = text[ index_i : index_f ]
    sample_size = len( sample )
    acceptables = profile.acceptable_characters
    rejectables = profile.rejectable_characters
    if 'Cc' in profile.rejectable_families:
        # Performance: Add C0 control characters to rejectables set.
        rejectables = rejectables | { chr( i ) for i in range( 0x20 ) }
    rejectable_families = profile.rejectable_families
    printables_min = sample_size * profile.printables_ratio_min
    rejectables_max = sample_size * profile.rejectables_ratio_max
    printables_count = 0
    rejectables_count = 0
    for c in sample:
        if c in acceptables: continue
        if c in rejectables: rejectables_count += 1
        else:
            ucat = __.unicodedata.category( c )
            if ucat in rejectable_families:
                rejectables_count += 1
            elif ucat[ 0 ] in _HYPERCATEGORIES_PRINTABLE:
                printables_count += 1
        if rejectables_count > rejectables_max: return False
    return printables_count >= printables_min
