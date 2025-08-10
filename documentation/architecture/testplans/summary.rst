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
Test Organization Summary
*******************************************************************************

Test Module Numbering Scheme
===============================================================================

This project follows a systematic numbering approach for test modules:

**000-099**: Package internals and utilities
  - ``test_000_package.py`` - Package-level functionality
  - ``test_010_base.py`` - Internal utilities and base functionality

**100-199**: Exception handling (Lower-level API)
  - ``test_100_exceptions.py`` - Exception classes and error handling

**200-299**: Core detection functionality (Lower-level API)
  - ``test_200_detection.py`` - Text detection functions (charset, MIME type, content validation)
  - ``test_210_lineseparators.py`` - Line separator enumeration and utilities

**300-399**: Reserved for higher-level integration functionality

Test Function Numbering
===============================================================================

Within each test module, functions are numbered by component:

- **000-099**: Basic functionality tests for the module
- **100-199, 200-299, etc.**: Each function/class gets its own 100-number block
- **Increments of 10-20**: For closely related test variations within a block

Example from ``test_200_detection.py``::

    def test_000_imports():
        ''' Basic module import verification '''

    def test_100_detect_charset_utf8():
        ''' charset detection with UTF-8 content '''

    def test_110_detect_charset_ascii():
        ''' charset detection with ASCII content '''

    def test_200_detect_mimetype_magic():
        ''' MIME type detection via magic numbers '''

    def test_210_detect_mimetype_extension():
        ''' MIME type detection via extension fallback '''

Project-Specific Testing Conventions
===============================================================================

Dependency Injection Preferred
-------------------------------------------------------------------------------

This codebase uses immutable objects that prevent monkey-patching. Use dependency injection patterns instead of patching internal code.

Test Data Organization
-------------------------------------------------------------------------------

- **Inline byte arrays preferred**: Most test data as inline ``b"content"`` in test code
- ``tests/data/samples/`` - Minimal binary fixtures only for complex cases (JPEG samples, etc.)

Coverage Goals
-------------------------------------------------------------------------------

- Target: 100% line and branch coverage
- Use ``# pragma: no cover`` only as last resort for untestable defensive code
- All public functions must have comprehensive test coverage

Performance Considerations
-------------------------------------------------------------------------------

- Use pyfakefs for filesystem operations when needed
- Prefer in-memory test data over file-based fixtures for simple cases
- Keep full test suite execution under 2 seconds

Rationale for Test Organization
===============================================================================

**Exception handling (100s)** gets lowest numbering as foundational error handling that all other components depend on.

**Core detection (200s)** for detection.py and lineseparators.py reflects their role as fundamental text processing utilities.

**Future higher numbering** (300s+) reserved for integration tests and higher-level functionality that builds on these core detection capabilities.