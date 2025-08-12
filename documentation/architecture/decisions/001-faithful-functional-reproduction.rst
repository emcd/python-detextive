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
001. Faithful Functional Reproduction
*******************************************************************************

Status
===============================================================================

Accepted

Context
===============================================================================

The detextive library must consolidate text detection functionality from
multiple packages (python-mimeogram, internal cache proxy, ai-experiments) while
providing drop-in replacement APIs. The existing implementations use functional
approaches with proven behavior patterns:

* **python-mimeogram**: Well-tested functions with complex parameter handling,
  UTF-8 bias, and extensible MIME type patterns
* **Internal cache proxy**: HTTP-focused functions with header parsing  
* **ai-experiments**: Simple utility functions with magic-based detection

The primary constraint for the first iteration is **minimal migration effort**.
Existing code must be able to replace function imports with no behavioral
changes, preserving all edge cases and detection heuristics that have been
validated in production use.

Secondary constraints include:
* Maintain exact existing behavior patterns and return types
* Preserve UTF-8 bias and validation logic from mimeogram implementation
* Support same dependency libraries (chardet, puremagic, mimetypes)
* Handle same edge cases (empty content, binary data, encoding validation)

Decision
===============================================================================

For the **first iteration**, we will implement a **Faithful Functional
Reproduction** that directly consolidates existing function implementations
without architectural changes.

Core components:

**Direct Function Consolidation:**

* ``detect_charset(content)`` - Consolidates charset detection with UTF-8 bias
* ``detect_mimetype(content, location)`` - Consolidates MIME detection with 
  fallback chains
* ``detect_mimetype_and_charset(content, location, *, mimetype=absent, 
  charset=absent)`` - Preserves complex parameter handling from mimeogram
* ``is_textual_mimetype(mimetype)`` - Consolidates textual MIME validation
* ``is_reasonable_text_content(content)`` - Preserves heuristic validation
* ``LineSeparators`` enum - Direct migration from mimeogram implementation

**Implementation Strategy:**
* Copy proven logic from mimeogram acquirers.py and parts.py  
* Consolidate variations from other packages as compatibility functions
* Maintain identical parameter signatures and return types
* Preserve all existing validation and fallback behavior

Alternatives
===============================================================================

**Object-Oriented Architecture with Classes**

*Benefits*: Better extensibility, testing isolation, configuration support
*Drawbacks*: Breaking API changes, implementation complexity, delayed delivery
*Rejection Reason*: Violates faithful reproduction requirement, adds complexity
not needed for consolidation goal

**Hybrid Functional-Object Architecture**  

*Benefits*: API compatibility with internal extensibility
*Drawbacks*: Over-engineering for consolidation task, premature optimization
*Rejection Reason*: Introduces unnecessary complexity for first iteration,
can be addressed in future iterations (see ADR-002)

**Configuration-Driven Factory Pattern**

*Benefits*: Maximum runtime flexibility  
*Drawbacks*: Significant API changes, over-engineering
*Rejection Reason*: Violates drop-in replacement requirement

**Do Nothing (Keep Duplication)**

*Benefits*: No work or risk
*Drawbacks*: Continued maintenance overhead, behavioral inconsistencies
*Rejection Reason*: Fails to address consolidation requirement

Consequences
===============================================================================

**Positive Consequences**

* **Zero Migration Risk**: Existing code works with simple import changes
* **Behavioral Fidelity**: Preserves all validated production behavior
* **Fast Delivery**: Direct consolidation enables rapid implementation
* **Testing Leverage**: Can reuse existing test patterns and edge cases
* **Dependency Stability**: Uses same proven dependencies without additions

**Negative Consequences**

* **Limited Extensibility**: Pure functional approach offers minimal 
  configuration or extension points
* **Code Duplication**: Some internal duplication may remain between similar
  functions
* **Testing Limitations**: Functional approach makes isolated unit testing 
  more challenging than class-based approaches

**Neutral Consequences**

* **Future Iterations**: Architecture can evolve in subsequent iterations
  without breaking existing usage
* **Documentation**: Straightforward functional API requires minimal learning
* **Performance**: Direct function calls provide optimal performance for
  simple use cases

**Implementation Implications**

* Focus implementation effort on exact behavior reproduction
* Consolidate only where behavior is identical across existing implementations
* Preserve parameter validation, error handling, and edge case logic
* Document any minor behavioral differences between consolidated sources
* Defer architectural improvements to future iterations (ADR-002)