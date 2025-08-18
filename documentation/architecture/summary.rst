.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+


*******************************************************************************
System Overview
*******************************************************************************

The **detextive** library implements a faithful functional reproduction to
consolidate text detection capabilities from multiple packages. The first
iteration prioritizes behavioral fidelity and minimal migration effort over
architectural sophistication.

Major Components
===============================================================================

Core Detection Functions
-------------------------------------------------------------------------------

**Public Functional API**
  Direct consolidation of proven functions providing drop-in compatibility:
  
  * ``detect_charset(content)`` - Character encoding with UTF-8 bias
  * ``detect_mimetype(content, location)`` - MIME type with fallback chains
  * ``detect_mimetype_and_charset(content, location, *, mimetype=absent, 
    charset=absent)`` - Complex parameter handling from mimeogram
  * ``is_textual_mimetype(mimetype)`` - Textual MIME type validation
  * ``is_reasonable_text_content(content)`` - Heuristic text vs binary

**Line Separator Processing**
  Direct migration of proven enumeration and utilities:
  
  * ``LineSeparators`` enum - Detection, normalization, and nativization methods

Component Relationships
===============================================================================

**Functional Architecture**

.. code-block::

    ┌─────────────────────────────────────────────────┐
    │             Public Functions                  │
    │  detect_mimetype()  detect_charset()  etc...    │
    └─────────────────────────────────────────────────┘
                            │
    ┌─────────────────────────────────────────────────┐
    │          Consolidated Detection Logic          │
    │     Faithful reproduction of existing logic     │
    └─────────────────────────────────────────────────┘
                            │
    ┌─────────────────────────────────────────────────┐
    │            External Dependencies               │
    │    chardet  puremagic  mimetypes (stdlib)      │
    └─────────────────────────────────────────────────┘

**Data Flow**

1. **Input Processing**: Functions receive byte content and optional metadata
2. **Direct Analysis**: Functions apply statistical analysis, pattern matching,
   and heuristics using consolidated logic from existing implementations  
3. **Validated Logic**: All detection behavior reproduced exactly from proven
   mimeogram, cache proxy, and ai-experiments implementations
4. **Output**: Identical return values and types as existing implementations

Integration Patterns
===============================================================================

**Drop-in Replacement Strategy**
  Existing code can replace imports with minimal changes:
  
  .. code-block:: python
  
      # Before: from mimeogram.acquirers import _detect_charset
      # After:  from detextive import detect_charset
      charset = detect_charset(content_bytes)

**Behavioral Fidelity**
  Preserves exact existing behavior:
  
  * UTF-8 bias with validation from mimeogram charset detection
  * Extensible textual MIME type patterns from all implementations
  * Fallback chains (puremagic → mimetypes) from mimeogram  
  * Complex parameter handling from ``detect_mimetype_and_charset``
  * Heuristic validation from ``is_reasonable_text_content``
  * Error handling and exception types maintained

**Implementation Strategy**
  * Direct consolidation of proven function logic
  * Minimal abstraction to preserve performance characteristics
  * Same dependencies and detection libraries as existing implementations

Architectural Patterns
===============================================================================

**Faithful Functional Reproduction**
  Direct consolidation of existing functional implementations without
  architectural changes (see ADR-001).

**Consolidation Pattern**
  Multiple implementations merged into single functions:
  
  * **chardet**: Statistical charset detection with UTF-8 bias
  * **puremagic**: Pure Python magic byte detection (primary)  
  * **mimetypes**: Standard library extension-based fallback
  * **LineSeparators**: Byte-level line ending detection and normalization

**v2.0 Evolution**
  ADR-003, ADR-004, and ADR-005 document the context-aware detection architecture 
  for v2.0 that addresses real-world integration challenges:
  
  * Context-driven detection utilizing HTTP headers, location, and content analysis
  * Error class provider pattern eliminating exception translation overhead
  * Configurable validation behaviors for performance and security requirements
  * Enhanced function interfaces maintaining backward compatibility

**Future Extensibility**
  ADR-002 documents potential future architectural enhancements:
  
  * Plugin architecture for alternative detection backends
  * Internal detector classes for advanced configuration and testing