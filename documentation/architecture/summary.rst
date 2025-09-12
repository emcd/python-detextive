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
  Core detection and inference functions with confidence-aware behavior:
  
  * ``detect_charset(content, *, behaviors=BEHAVIORS_DEFAULT, ...)`` - Character encoding detection
  * ``detect_charset_confidence(content, *, behaviors=BEHAVIORS_DEFAULT, ...)`` - Charset detection with confidence scoring  
  * ``detect_mimetype(content, *, behaviors=BEHAVIORS_DEFAULT, ...)`` - MIME type detection
  * ``detect_mimetype_confidence(content, *, behaviors=BEHAVIORS_DEFAULT, ...)`` - MIME type detection with confidence scoring
  * ``infer_charset(content, *, behaviors=BEHAVIORS_DEFAULT, ...)`` - Charset inference with validation
  * ``infer_charset_confidence(content, *, behaviors=BEHAVIORS_DEFAULT, ...)`` - Charset inference with confidence scoring
  * ``infer_mimetype_charset(content, *, behaviors=BEHAVIORS_DEFAULT, ...)`` - Combined MIME type and charset inference
  * ``decode(content, *, behaviors=BEHAVIORS_DEFAULT, ...)`` - High-level bytes-to-text decoding with validation
  * ``is_textual_mimetype(mimetype)`` - Textual MIME type validation  
  * ``is_valid_text(text, profile=PROFILE_TEXTUAL)`` - Unicode-aware text validation

**Core Types and Configuration**
  Shared data structures for confidence-aware behavior:
  
  * ``Result(value, confidence)`` - Detection results with confidence scoring (0.0-1.0)
  * ``Behaviors`` - Configurable detection behavior with confidence thresholds  
  * ``BehaviorTristate`` - When to apply behaviors (Never/AsNeeded/Always)
  * ``CodecSpecifiers`` - Dynamic codec resolution (FromInference/OsDefault/etc.)

**Text Validation System**
  Unicode-aware text validation with configurable profiles:
  
  * ``TextValidationProfile`` - Validation rules and character acceptance policies
  * ``PROFILE_TEXTUAL`` - General textuality validation (lenient)
  * ``PROFILE_TERMINAL_SAFE`` - Terminal output safety (strict)
  * ``PROFILE_PRINTER_SAFE`` - Printer output safety (form feed allowed)

**Line Separator Processing**
  Direct migration of proven enumeration and utilities:
  
  * ``LineSeparators`` enum - Detection, normalization, and nativization methods

Component Relationships
===============================================================================

**v2.0 Layered Architecture**

.. code-block::

    ┌─────────────────────────────────────────────────┐
    │        Public API Layer (decoders.py)         │
    │  decode() - High-level bytes-to-text function  │
    └─────────────────────────────────────────────────┘
                            │
    ┌─────────────────────────────────────────────────┐
    │     Inference Layer (inference.py)            │
    │  infer_charset_confidence()  infer_mimetype()   │
    │  Context-aware orchestration + HTTP parsing    │
    └─────────────────────────────────────────────────┘
                            │
    ┌─────────────────────────────────────────────────┐
    │   Detection Layer (detectors.py)              │
    │  detect_charset_confidence()  detect_mimetype() │
    │  Core detection with confidence scoring        │
    └─────────────────────────────────────────────────┘
                            │
    ┌─────────────────────────────────────────────────┐
    │  Support Modules (charsets.py, validation.py) │
    │  Trial decoding + Text validation + MIME utils │
    └─────────────────────────────────────────────────┘
                            │
    ┌─────────────────────────────────────────────────┐
    │            External Dependencies               │
    │    chardet  puremagic  mimetypes (stdlib)      │
    └─────────────────────────────────────────────────┘

**v2.0 Data Flow**

1. **Input Processing**: Functions receive byte content, behaviors configuration, and optional HTTP/location context
2. **Confidence-Aware Detection**: Core detectors return Result objects with confidence scores using chardet/puremagic
3. **Smart Decision Making**: Confidence thresholds drive AsNeeded behavior for trial decode and text validation  
4. **Layered Inference**: Higher-level functions orchestrate detection, validation, and error handling
5. **Validated Output**: Text validation ensures decoded content meets specified profiles for safety/quality

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