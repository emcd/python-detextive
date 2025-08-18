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
   | distribute under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+


*******************************************************************************
004. Error Class Provider Pattern
*******************************************************************************

Status
===============================================================================

Accepted

Context
===============================================================================

Analysis of downstream package integration revealed that exception translation 
represents a major integration friction point. Current integration patterns 
require extensive boilerplate code at every call site to translate detextive 
exceptions into downstream exception hierarchies.

**Current Integration Tax:**

.. code-block:: python

    # Current: 8+ lines of boilerplate per call site
    try:
        mimetype, charset = detect_mimetype_and_charset(content_bytes, location)
        if not is_textual_content(content_bytes):
            raise DocumentationInaccessibility(url_s, "Non-textual data")
    except TextualMimetypeInvalidity as exc:
        raise DocumentationInaccessibility(url_s, str(exc)) from exc

This pattern violates DRY principles and creates maintenance overhead when 
exception hierarchies evolve. The pattern is repeated across multiple call 
sites within the same package and across different downstream packages.

**Requirements Analysis:**

* **Zero Boilerplate**: Eliminate need for try/catch/re-raise patterns
* **Flexible Error Handling**: Support graceful degradation, native exceptions, and custom hierarchies
* **Context Preservation**: Maintain original error context and location information in translated exceptions
* **Type Safety**: Enable static analysis of exception handling patterns

**Architectural Forces:**

* Need to maintain detextive's internal exception hierarchy for clarity
* Want to eliminate integration friction without compromising error information
* Must support diverse downstream error handling strategies
* Should enable gradual migration from current exception handling patterns

Decision
===============================================================================

We will implement an **Error Class Provider Pattern** that enables call-site 
control over exception handling through a provider function parameter.

**Core Pattern Design:**

.. code-block:: python

    ErrorClassProvider: TypeAlias = Callable[[str], type[Exception]]

    def detect_mimetype_charset(
        content: Content,
        location: Absential[Location] = absent, *,
        # ... other parameters ...
        error_class_provider: Absential[ErrorClassProvider] = absent,
    ) -> tuple[Absential[str], Absential[str]]:

**Three-Way Error Semantics:**

* **None**: Return ``absent`` values instead of raising exceptions (graceful degradation)
* **absent**: Use detextive's native exception hierarchy (default, current behavior)  
* **Callable**: Map exception names to downstream exception classes via provider function

**Provider Function Interface:**

The provider function receives detextive's internal exception class name and 
returns the corresponding downstream exception class:

.. code-block:: python

    # Example provider for DocumentationInaccessibility mapping
    def map_to_doc_errors(exception_name: str) -> type[Exception]:
        return DocumentationInaccessibility

    # Usage eliminates all boilerplate
    mimetype, charset = detect_mimetype_charset(
        content_bytes, location,
        error_class_provider=map_to_doc_errors
    )

**Implementation Strategy:**

* Internal exception handling logic checks error_class_provider parameter
* When provider is callable, exceptions are mapped before raising
* Original exception context preserved through ``from`` chaining
* Provider function called with detextive exception class name for flexibility

Alternatives
===============================================================================

**Exception Mapping Dictionary**

*Benefits*: Simple mapping structure, clear exception relationships
*Drawbacks*: Requires pre-definition of all possible exception mappings
*Rejection Reason*: Less flexible than callable pattern, harder to maintain

**Exception Wrapper Classes**

*Benefits*: Preserves full exception hierarchy, maintains type relationships
*Drawbacks*: Complex wrapper implementation, unclear exception handling
*Rejection Reason*: Over-engineering for mapping use case

**Global Exception Configuration**

*Benefits*: One-time configuration affects all function calls
*Drawbacks*: Global state, less flexible per-call control
*Rejection Reason*: Global state conflicts with functional approach

**Result Pattern with Union Types**

*Benefits*: No exceptions, explicit success/failure handling
*Drawbacks*: Breaking change to all function signatures, Python typing complexity
*Rejection Reason*: Violates backward compatibility requirement

Consequences
===============================================================================

**Positive Consequences**

* **Zero Boilerplate**: Eliminates try/catch/re-raise patterns entirely
* **Flexible Error Handling**: Supports three distinct error handling strategies
* **Context Preservation**: Original error information maintained through exception chaining
* **Gradual Migration**: Existing code continues working while new integration patterns become available
* **Type Safety**: Provider pattern enables static analysis of exception flows

**Negative Consequences**

* **Interface Complexity**: Additional parameter increases function signature complexity
* **Learning Curve**: New pattern requires documentation and examples
* **Testing Complexity**: Must test all three error handling modes
* **Provider Function Design**: Requires careful design for reusable provider functions

**Neutral Consequences**

* **Documentation Requirements**: Enhanced error handling requires comprehensive examples
* **Migration Strategy**: Teams can migrate incrementally to new pattern
* **Performance**: Negligible overhead for provider function calls

**Implementation Guidance**

**Provider Function Design Patterns:**

.. code-block:: python

    # Simple mapping: all detextive exceptions → single downstream exception
    lambda name: DocumentationInaccessibility

    # Conditional mapping: specific exceptions → specific downstream classes
    def custom_error_provider(exception_name: str) -> type[Exception]:
        mapping = {
            'CharsetDetectFailure': EncodingError,
            'TextualMimetypeInvalidity': ContentTypeError,
        }
        return mapping.get(exception_name, GenericProcessingError)

**Integration with Existing Functions:**

All v2.0 detection functions will support the error_class_provider parameter 
with identical semantics, providing consistent exception handling across the 
entire API surface.

**Backward Compatibility:**

The default behavior (error_class_provider=absent) preserves current exception 
behavior exactly, ensuring zero breaking changes for existing integrations.

This decision establishes a reusable pattern that can be applied across other 
packages in the ecosystem for consistent exception handling strategy.