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
Release Notes
*******************************************************************************

.. towncrier release notes start

detextive 2.0 (2025-09-20)
==========================

Enhancements
------------

- API: Add comprehensive type aliases for function arguments with PEP 593 annotations for improved API documentation and semantic clarity.
- API: Add confidence-based detection with new functions ``detect_charset_confidence()``, ``detect_mimetype_confidence()``, ``infer_charset_confidence()``, and ``infer_mimetype_charset_confidence()`` returning Result objects with confidence scores.
- API: Enhance ``decode()`` function with intelligent MIME type validation, graceful error fallback, and single-pass decoding efficiency.
- API: Implement comprehensive text validation system with Unicode-aware profiles including TEXTUAL, TERMINAL, TERMINAL_ANSI, and PRINTER configurations.
- Platform: Improve Windows compatibility by using python-magic-bin to avoid Cygwin buffer issues and handle MIME type detection differences.


Notices
-------

- API: Rename ``detect_mimetype_and_charset()`` to ``infer_mimetype_charset()`` and ``is_textual_content()`` to ``is_valid_text()`` for improved clarity.


Detextive 1.0 (2025-08-12)
==========================

Enhancements
------------

- Provide ``LineSeparators`` enum with detection, normalization, and nativization
  methods.
- Provide ``detect_charset``, ``detect_mimetype``,
  ``detect_charset_and_mimetype``, ``is_textual_mimetype``, and
  ``is_textual_content``.
