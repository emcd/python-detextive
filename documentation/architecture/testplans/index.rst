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
Test Plans
*******************************************************************************

This section contains comprehensive test planning documentation for the detextive library, including test organization conventions, coverage strategies, and detailed implementation plans for achieving 100% test coverage.

Test plans follow systematic approaches based on the project's testing principles:

- **Dependency injection over monkey-patching** for testable code architecture
- **100% line and branch coverage** as the standard goal
- **Performance-conscious resource use** with in-memory testing strategies
- **Systematic test organization** with numbered modules and functions

.. toctree::
   :maxdepth: 2

   summary
   core-functionality


Overview
===============================================================================

The test planning process systematically addresses:

**Coverage Gap Analysis**
  Identification of all uncovered lines and untested functionality across modules

**Test Strategy Development**
  Comprehensive approaches for testing each function, class, and method with appropriate test data strategies

**Implementation Guidance**
  Detailed plans for achieving full coverage while following project testing principles

**Architectural Considerations**
  Analysis of testability constraints and recommendations for maintaining clean, testable code

Current Test Plans
===============================================================================

:doc:`summary`
  Test organization conventions, numbering schemes, and project-specific testing guidelines

:doc:`core-functionality`
  Detailed test plan for ``detection.py`` and ``lineseparators.py`` modules targeting 100% coverage

Future Test Plans
===============================================================================

Additional test plans will be added to this directory as new modules are developed or existing modules require comprehensive test coverage analysis.