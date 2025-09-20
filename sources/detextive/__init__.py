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


''' Detects textual content. '''


from . import __

from .charsets import *
from .core import *
from .decoders import *
from .detectors import *
from .inference import *
from .lineseparators import *
from .mimetypes import *
from .validation import *

# --- BEGIN: Injected by Copier ---
from . import exceptions
# --- END: Injected by Copier ---


__version__ = '2.0'


__.immut.finalize_module( __name__, recursive = True )
