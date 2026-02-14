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

The **detextive** library consolidates MIME detection, charset inference,
text decoding, and line-separator utilities behind a unified functional API.

Major Components
===============================================================================

Public API
-------------------------------------------------------------------------------

The public API is composed of confidence-aware detection functions,
inference orchestration functions, and high-level decode functions:

* ``detect_charset`` / ``detect_charset_confidence``
* ``detect_mimetype`` / ``detect_mimetype_confidence``
* ``infer_charset`` / ``infer_charset_confidence``
* ``infer_mimetype_charset`` / ``infer_mimetype_charset_confidence``
* ``decode``
* ``decode_inform``
* ``is_textual_mimetype``
* ``is_valid_text``
* ``LineSeparators`` utilities

Core Types and Configuration
-------------------------------------------------------------------------------

* ``Behaviors`` - policy object controlling parse/detect/trial/validation
  behaviors and confidence thresholds.
* ``BehaviorTristate`` - execution mode for selected behavior paths
  (Never/AsNeeded/Always).
* ``DetectFailureActions`` - fallback policy on detector failure
  (Default/Error).
* ``CodecSpecifiers`` - dynamic trial codec slots
  (FromInference/OsDefault/PythonDefault/UserSupplement).
* ``CharsetResult`` - charset with confidence score.
* ``MimetypeResult`` - MIME type with confidence score.
* ``DecodeInformResult`` - decoded text plus charset/mimetype/line-separator
  metadata.

Layered Runtime Architecture
===============================================================================

.. code-block:: text

    ┌──────────────────────────────────────────────────────┐
    │ Public API (__init__.py re-exports)                 │
    └──────────────────────────────────────────────────────┘
                          │
    ┌──────────────────────────────────────────────────────┐
    │ Decoding Layer (decoders.py)                        │
    │ decode(), decode_inform()                           │
    │ - HTTP Content-Type parse + charset-first attempt   │
    │ - detector-assisted trial decode + text validation  │
    │ - optional MIME/line-separator metadata             │
    └──────────────────────────────────────────────────────┘
                          │
    ┌──────────────────────────────────────────────────────┐
    │ Inference Layer (inference.py)                      │
    │ infer_*() orchestration + header/location context   │
    └──────────────────────────────────────────────────────┘
                          │
    ┌──────────────────────────────────────────────────────┐
    │ Detection Layer (detectors.py)                      │
    │ detector registries + confidence results            │
    └──────────────────────────────────────────────────────┘
                          │
    ┌──────────────────────────────────────────────────────┐
    │ Support Layer                                        │
    │ charsets.py, mimetypes.py, validation.py,           │
    │ lineseparators.py                                   │
    └──────────────────────────────────────────────────────┘

Decoder Flow (v3)
===============================================================================

``decode`` and ``decode_inform`` share the same decoding core:

1. Parse ``http_content_type`` when provided.
2. If header MIME is non-textual, raise ``ContentDecodeImpossibility``.
3. If header charset is textual and decodable, decode with that charset first.
4. Otherwise, run detector-assisted trial decodes in configured codec order.
5. Apply text validation according to ``Behaviors.text_validate`` and
   ``Behaviors.text_validate_confidence``.
6. Return text (``decode``) or structured metadata (``decode_inform``).

Inference Flow
===============================================================================

``infer_*`` functions use contextual hints and detection orchestration:

1. Optionally parse ``http_content_type`` depending on behavior settings.
2. Consider ``location``-based MIME hints.
3. Run registered detectors for MIME and charset as configured.
4. Apply ``*_default`` values only for fallback return semantics.
5. Use ``*_supplement`` values as hints to guide detection/validation.

Integration Notes
===============================================================================

* ``decode`` is authoritative for byte-to-text conversion and raises on
  irrecoverable decode failure.
* ``decode_inform`` is intended for callers that need text plus consistent
  decode metadata in one call.
* Detector registries are pluggable and backend-optional by design.
* Trial codec ordering is behavior-driven and can be overridden by callers.
