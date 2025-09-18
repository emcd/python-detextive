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

Overview
===============================================================================

This section contains comprehensive test planning documentation, including test
organization conventions, coverage strategies, and detailed implementation
plans for achieving systematic test coverage.

Test plans follow project testing principles described in the `common test
development guidelines
<https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/tests.rst>`_.
Key principles include:

- **Dependency injection over monkey-patching** for testable code architecture
- **Systematic coverage analysis** with clear gap identification
- **Performance-conscious resource use** with appropriate testing strategies
- **Organized test structure** with numbered modules and functions

Test Planning Process
===============================================================================

The test planning process systematically addresses:

**Coverage Gap Analysis**
  Identification of all uncovered lines and untested functionality across modules

**Test Strategy Development**
  Comprehensive approaches for testing each function, class, and method with
  appropriate test data strategies

**Implementation Guidance**
  Detailed plans for achieving coverage while following project testing principles

**Architectural Considerations**
  Analysis of testability constraints and recommendations for maintaining
  clean, testable code

Test Module Numbering Scheme
===============================================================================

This project follows a systematic numbering approach for test modules:

**000-099**: Package internals and utilities
  - ``test_000_package.py`` - Package-level functionality
  - ``test_010_base.py`` - Internal utilities and base functionality

**100-199**: Core types and exceptions (Lower-level API)
  - ``test_100_nomina.py`` - Type aliases and common definitions (optional)
  - ``test_110_exceptions.py`` - Exception classes and location parameter handling
  - ``test_120_core.py`` - Core types, enums, behaviors, and result types

**200-299**: Utility components (Lower-level API)
  - ``test_200_lineseparators.py`` - Line separator detection and normalization
  - ``test_210_mimetypes.py`` - MIME type utility functions
  - ``test_220_charsets.py`` - Charset detection utilities and codec handling

**300-399**: Validation and detection (Mid-level API)
  - ``test_300_validation.py`` - Text validation and reasonableness checking
  - ``test_310_detectors.py`` - Core detection functions with default return behavior

**400-499**: Inference and integration (Higher-level API)
  - ``test_400_inference.py`` - Context-aware inference functions

**500-599**: High-level functionality (Top-level API)
  - ``test_500_decoders.py`` - High-level decoding and integration functions

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

Test Data Organization
-------------------------------------------------------------------------------

- **Centralized content patterns**: ``tests/test_000_detextive/patterns.py`` provides curated byte sequences
- **No filesystem dependencies**: All test content provided via patterns module
- **Cross-platform compatibility**: Platform-specific detection variants included
- **Comprehensive coverage**: Patterns for charset detection, MIME types, line separators, validation

**Content Pattern Categories:**
- UTF-8, ASCII, Latin-1, Windows-1252 charset samples
- Text, JSON, binary magic byte samples
- Unix, Windows, Mac line separator patterns
- Validation patterns (reasonable text, control characters, binary)
- Error condition patterns (undetectable content, decode failures)
- Windows compatibility patterns (python-magic vs python-magic-bin differences)

Version 2.0 Testing Focus
-------------------------------------------------------------------------------

**Critical Priority - Default Return Behavior:**
- ``DetectFailureActions.Default`` vs ``DetectFailureActions.Error`` testing
- Default parameter validation and confidence scoring (must be 0.0 for failures)
- Mixed failure behaviors (charset defaults, mimetype errors)
- Lines 97-101, 149-155 in detectors.py (currently 0% coverage)

**High Priority:**
- Exception handling with location parameters
- Enhanced inference functions with new default parameters
- New default parameter paths in decoders.py
- Cross-platform compatibility (python-magic vs python-magic-bin)

**Testing Conventions:**
- Dependency injection over monkey-patching (immutable objects prevent patching)
- pyfakefs for filesystem operations (when needed)
- Property-based testing for behavioral invariants
- Cross-platform expected outcomes for Windows compatibility
