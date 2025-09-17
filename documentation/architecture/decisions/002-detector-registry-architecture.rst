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
002. Detector Registry Architecture
*******************************************************************************

Status
===============================================================================

Implemented

Context
===============================================================================

Following the successful implementation of the faithful functional reproduction
(ADR-001), the v2.0 architecture required enhanced extensibility, configuration,
and testing capabilities. The initial functional approach, while sufficient for
consolidation, had identified limitations for advanced use cases:

**Identified Limitations:**
* Limited configuration options for detection parameters
* Difficult to isolate components for comprehensive unit testing
* No plugin architecture for alternative detection backends
* Hard-coded patterns and thresholds without runtime configuration
* Functional approach made performance optimization challenging

**Required Capabilities:**
* Support for configurable detection backend precedence
* Pluggable detection backends with graceful degradation
* Comprehensive testing of edge cases with isolated components
* Enhanced configuration through structured behavior objects
* Result consolidation for operations requiring multiple detection types

**Architectural Forces:**
* Maintain backward compatibility with functional API established in ADR-001
* Enable advanced configuration without complexity for simple use cases
* Support multiple detection libraries with graceful degradation when unavailable
* Provide testable, isolated components for comprehensive testing

Decision
===============================================================================

We implemented a **Detector Registry Architecture** in v2.0 that provides
pluggable backend support while maintaining full functional API compatibility.

**Core Architecture Components:**

**Detector Registry System:**
* ``CharsetDetector`` and ``MimetypeDetector`` type aliases define pluggable function interfaces
* ``charset_detectors`` and ``mimetype_detectors`` module-level registry dictionaries
* Dynamic detector registration system with automatic dependency discovery
* User-configurable detector precedence via ``Behaviors.charset_detectors_order`` and ``mimetype_detectors_order``

**Optional Dependency Management:**
* Lazy import pattern with graceful ``ImportError`` handling for optional libraries
* ``NotImplemented`` return pattern enables detection chain fallbacks
* Built-in support for ``charset-normalizer``, ``chardet``, ``python-magic``, and ``puremagic``
* Automatic fallback chains when preferred detectors are unavailable

**Enhanced Configuration System:**
* ``Behaviors`` dataclass provides structured configuration for all detection parameters
* Confidence-based detection thresholds and validation control through ``BehaviorTristate``
* Context-aware detection utilizing HTTP headers and file location information
* Per-detector configuration and failure handling modes

**Implementation Details:**

The registry system in ``detectors.py`` implements:

.. code-block:: python

    # Type aliases for pluggable detection functions
    CharsetDetector: TypeAlias = Callable[
        [Content, Behaviors], CharsetResult | NotImplementedType]
    MimetypeDetector: TypeAlias = Callable[
        [Content, Behaviors], MimetypeResult | NotImplementedType]

    # Module-level registries for dynamic detector management
    charset_detectors: Dictionary[str, CharsetDetector] = Dictionary()
    mimetype_detectors: Dictionary[str, MimetypeDetector] = Dictionary()

    # Example detector registration with graceful dependency handling
    def _detect_via_chardet(content, behaviors):
        try: import chardet
        except ImportError: return NotImplemented
        # ... detection logic
    charset_detectors['chardet'] = _detect_via_chardet

**Backward Compatibility Preservation:**
* All existing functional APIs maintain identical signatures and behavior
* Enhanced capabilities available through optional ``Behaviors`` parameters
* Zero breaking changes to existing usage patterns from ADR-001
* Performance characteristics preserved for simple detection use cases

Alternatives
===============================================================================

**Keep Pure Functional Architecture**

*Benefits*: Simplicity, no additional complexity, proven consolidation approach
*Drawbacks*: Limited extensibility, testing challenges, no backend configurability
*Rejection Reason*: Real-world integration requirements demanded configurable backend precedence

**Full Object-Oriented Refactoring**

*Benefits*: Maximum extensibility from start, comprehensive testability, rich API surface
*Drawbacks*: Violates ADR-001 faithful reproduction, breaking changes to functional API
*Rejection Reason*: Conflicts with backward compatibility requirement, unnecessary complexity

**Entry Point Plugin Architecture**

*Benefits*: Third-party extensibility, standardized plugin discovery, maximum flexibility
*Drawbacks*: Over-engineering, complex API, significant learning curve
*Rejection Reason*: Internal detector registry sufficient for identified requirements

Consequences
===============================================================================

**Positive Consequences**

* **Enhanced Extensibility**: Pluggable backend system enables support for multiple detection libraries
* **Configuration Flexibility**: Structured ``Behaviors`` configuration provides fine-grained control over detection logic
* **Graceful Degradation**: Optional dependency system ensures functionality even when preferred libraries unavailable
* **Testing Isolation**: Registry architecture enables comprehensive testing of individual detector components
* **Performance Optimization**: Configurable detector ordering optimizes for speed vs accuracy trade-offs
* **Backward Compatibility**: Zero breaking changes preserve existing functional API usage patterns

**Negative Consequences**

* **Implementation Complexity**: Registry system and configuration objects increase codebase complexity
* **Learning Curve**: Advanced configuration options require understanding of ``Behaviors`` and detector precedence
* **Testing Matrix**: Multiple detector combinations create larger test space requiring systematic coverage
* **Dependency Management**: Optional import handling requires careful error handling and fallback logic

**Neutral Consequences**

* **API Surface Growth**: Enhanced capabilities available through optional parameters without mandatory complexity
* **Performance Characteristics**: Simple use cases maintain identical performance while advanced features add configurability overhead
* **Migration Path**: Enhanced architecture provides foundation for future extensibility without disrupting existing integrations

**Implementation Results**

The detector registry architecture successfully addresses the extensibility limitations identified in the v1.x functional approach:

* **Configurable Backend Precedence**: ``charset_detectors_order`` and ``mimetype_detectors_order`` enable runtime detector selection
* **Isolated Component Testing**: Individual detectors can be tested independently through registry injection
* **Optional Dependency Support**: Graceful degradation when ``python-magic``, ``chardet``, etc. unavailable
* **Enhanced Configuration**: ``Behaviors`` dataclass provides structured, documented configuration options
* **Performance Flexibility**: Detector ordering enables optimization for different use case requirements

**Integration with v2.0 Architecture**

This implementation directly enabled the context-aware detection capabilities documented in ADR-003 by providing:
* Multiple backend support for improved detection accuracy
* Configuration foundation for validation behavior control (ADR-005)
* Registry architecture for default return behavior pattern (ADR-006)
* Structured foundation for future architectural enhancements