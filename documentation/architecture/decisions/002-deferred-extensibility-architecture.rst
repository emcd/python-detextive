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
002. Deferred Extensibility Architecture  
*******************************************************************************

Status
===============================================================================

Proposed (Deferred to Future Iteration)

Context
===============================================================================

After successful implementation of the faithful functional reproduction 
(ADR-001), future iterations may benefit from enhanced extensibility,
configuration, and testing capabilities. The current functional approach, 
while sufficient for consolidation, has limitations for advanced use cases:

**Current Limitations:**
* Limited configuration options for detection parameters  
* Difficult to isolate components for comprehensive unit testing
* No plugin architecture for alternative detection backends
* Hard-coded patterns and thresholds without runtime configuration
* Functional approach makes performance optimization challenging

**Future Requirements:**
* Support for custom MIME type patterns and detection rules
* Configurable charset detection confidence thresholds
* Pluggable detection backends (e.g., alternative to puremagic)
* Comprehensive testing of edge cases with isolated components
* Performance optimization through caching and lazy initialization
* Result consolidation for operations requiring multiple detection types

**Architectural Forces:**
* Need to maintain backward compatibility with functional API
* Want to enable advanced configuration without complexity for simple use cases
* Performance optimization may require stateful caching and initialization
* Comprehensive testing requires testable, isolated components

Decision
===============================================================================

**DEFERRED** until ADR-001 implementation is complete and validated in production.

When implemented in a future iteration, we propose a **Hybrid Functional-Object
Architecture** that maintains the existing functional API while adding internal
extensibility:

**Proposed Components:**

*Public Functional API (Unchanged):*
* Existing functions maintain identical signatures and behavior
* No breaking changes to code using ADR-001 implementation

*Internal Architecture Enhancements:*
* ``MimeDetector`` class - Configurable MIME detection with pluggable backends
* ``CharsetDetector`` class - Statistical analysis with configurable thresholds  
* ``LineSeparatorDetector`` class - Enhanced line ending detection
* ``DetectionResult`` class - Consolidated result object for multi-value operations
* Configuration system for detection parameters and pattern registration

*Integration Pattern:*
* Functional API delegates to lazily-initialized internal detector instances
* Configuration passed through detector constructors or global configuration
* Backward compatibility maintained through facade pattern over internal objects

Alternatives
===============================================================================

**Keep Functional Architecture Forever**

*Benefits*: Simplicity, no additional complexity, proven approach
*Drawbacks*: Limited extensibility, testing challenges, no advanced features
*Assessment*: May be adequate if no advanced requirements emerge

**Immediate Full Refactoring to Classes**

*Benefits*: Maximum extensibility from start, comprehensive testability  
*Drawbacks*: Violates ADR-001 faithful reproduction, premature optimization
*Rejection Reason*: Conflicts with iterative approach, unnecessary complexity
for consolidation goal

**Plugin Architecture with Registry**

*Benefits*: Maximum flexibility, third-party extensibility
*Drawbacks*: Over-engineering, complex API, steep learning curve
*Assessment*: Likely unnecessary unless clear plugin requirements emerge

Consequences
===============================================================================

**Benefits of Deferral:**

* **Risk Reduction**: ADR-001 provides proven foundation before architectural
  enhancement
* **User Feedback**: Real usage patterns inform architectural decisions
* **Iterative Development**: Allows validation of consolidation before
  extensibility
* **Resource Focus**: Full effort on consolidation and migration first

**Costs of Deferral:**

* **Refactoring Work**: Future implementation may require internal refactoring
* **Feature Limitations**: Advanced configuration unavailable in first iteration
* **Testing Challenges**: Functional approach may limit comprehensive test
  coverage initially

**Future Implementation Considerations:**

* Maintain strict backward compatibility with ADR-001 functional API
* Implement internal architecture changes without breaking existing usage
* Provide migration path for users wanting advanced features
* Consider performance implications of adding object layer over functions

**Decision Triggers for Implementation:**

This ADR should be revisited when:
* ADR-001 implementation is stable and adopted across target packages
* Users request configuration options not feasible with functional approach
* Testing gaps emerge that require component isolation
* Performance optimization needs arise that require stateful implementation
* Clear requirements emerge for pluggable backends or custom detection rules

**Implementation Strategy (When Activated):**

1. Implement internal detector classes maintaining functional API compatibility
2. Add configuration options through optional parameters or global configuration  
3. Enhance testing with isolated component tests
4. Add consolidated result objects for multi-value operations
5. Document migration path for users wanting advanced features
6. Maintain functional API as primary interface for simple use cases