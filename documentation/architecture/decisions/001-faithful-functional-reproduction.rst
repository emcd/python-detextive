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

Superseded

**Superseded By:** Version 2.0 implementation evolved significantly beyond faithful 
reproduction. The sophisticated behavior configuration, context-aware detection, 
and enhanced function interfaces represent a new architectural paradigm that 
transcends simple consolidation of existing implementations.

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

**Direct Function Consolidation (2.0 Implementation):**

* ``detect_charset(content, /, *, behaviors=default, default=absent, mimetype=absent, location=absent)`` - Enhanced charset detection with configurable behaviors
* ``detect_mimetype(content, /, *, behaviors=default, charset=absent, location=absent)`` - Enhanced MIME detection with context awareness
* ``infer_mimetype_charset(content, /, *, behaviors=default, http_content_type=absent, location=absent, charset_default=absent, mimetype_default=absent)`` - Comprehensive inference with HTTP context support
* ``is_textual_mimetype(mimetype)`` - Consolidates textual MIME validation
* ``LineSeparators`` enum - Enhanced line separator handling

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