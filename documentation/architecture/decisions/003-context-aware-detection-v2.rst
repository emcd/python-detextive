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
003. Context-Aware Detection Architecture v2.0
*******************************************************************************

Status
===============================================================================

Accepted

Context
===============================================================================

Real-world integration analysis from downstream packages (librovore) revealed 
fundamental limitations in the v1.x functional API that create significant 
integration burden. The primary integration pain points identified include:

**Redundant Detection Operations**: Current integration patterns require multiple
function calls for comprehensive detection workflows, creating performance
overhead and code complexity.

**Redundant Detection Overhead**: Multiple function calls perform overlapping 
content analysis (detect_mimetype_and_charset + is_textual_content), resulting 
in performance penalties for comprehensive detection workflows.

**Context Loss**: Available HTTP headers cannot be utilized in current API, 
forcing downstream packages to implement custom fallback logic that duplicates 
detection functionality.

**Validation Rigidity**: No control over which validations occur when, leading 
to unnecessary computational work and inappropriate error handling for specific 
use cases.

These limitations violate the core product requirement (REQ-005) of providing 
drop-in replacement interfaces that minimize migration effort. The current 
functional reproduction approach successfully consolidated duplicate 
implementations but created new integration friction for context-rich 
environments.

Decision
===============================================================================

For **v2.0**, we will implement a **Context-Aware Detection Architecture** 
that addresses real-world integration challenges while maintaining backward 
compatibility with enhanced function implementations.

**Core Architectural Components:**

**Enhanced Function Interface:**
* ``detect_charset(content, /, *, behaviors=default, default=absent, mimetype=absent, location=absent)`` - Enhanced charset detection with configurable behaviors
* ``infer_mimetype_charset(content, /, *, behaviors=default, http_content_type=absent, location=absent, ...)`` - Primary combined detection with HTTP context support
* ``detect_mimetype(content, /, *, behaviors=default, charset=absent, location=absent)`` - Focused MIME type detection

**Context-Driven Detection Strategy:**
* HTTP Content-Type headers processed first when available via ``http_content_type`` parameter
* Location/filename extension analysis as secondary fallback  
* Magic bytes content analysis as final fallback
* Detection methods selected automatically based on available context and ``Behaviors`` configuration

**Configurable Validation Behaviors:**
* ``Behaviors`` dataclass controls validation execution (trial_decode, validate_printable)
* ``printable_threshold`` parameter for character validation tolerance
* Conditional execution prevents unnecessary validation overhead

**Confidence-Based Result Types:**
* ``CharsetResult(charset, confidence)`` for charset detection results
* ``MimetypeResult(mimetype, confidence)`` for MIME type detection results
* Confidence scoring enables AsNeeded behavior and quality assessment

**Backward Compatibility Strategy:**
* Existing v1.x functions enhanced with new capabilities while preserving signatures
* No breaking changes to current function behavior
* Enhanced capabilities available through optional parameters

Alternatives
===============================================================================

**Comprehensive Detection Result Object**

*Benefits*: Single detection call returns structured result with metadata
*Drawbacks*: Heavy-weight object for simple use cases, complex field interpretation
*Rejection Reason*: Over-engineering for typical workflows requiring simple tuple returns

**Plugin Architecture in v2.0**

*Benefits*: Maximum extensibility, support for alternative detection backends
*Drawbacks*: Significant complexity increase, premature optimization
*Rejection Reason*: Architectural scope too large, deferred to future iteration

**Separate v2.0 Package**

*Benefits*: Clean API design without backward compatibility constraints
*Drawbacks*: Ecosystem fragmentation, migration complexity
*Rejection Reason*: Violates consolidation goal, creates maintenance burden

**Function Overload Pattern**

*Benefits*: Multiple function signatures for different use cases
*Drawbacks*: Python typing complexity, unclear function selection
*Rejection Reason*: Less maintainable than optional parameters with clear defaults

Consequences
===============================================================================

**Positive Consequences**

* **Unified Detection**: Single function calls provide comprehensive detection with confidence scoring
* **Context Fusion**: Single detection call leverages all available context (HTTP headers, location, content)
* **Performance Optimization**: Conditional validation prevents unnecessary computational overhead
* **Backward Compatibility**: Existing code continues working with enhanced capabilities
* **Integration Simplification**: Common integration patterns require minimal code

**Negative Consequences**

* **Interface Complexity**: Additional optional parameters increase cognitive load
* **Implementation Complexity**: Context-driven detection requires sophisticated internal logic
* **Testing Matrix**: Behaviors combinations create large test space requiring systematic coverage
* **Documentation Overhead**: Enhanced capabilities require comprehensive usage documentation

**Neutral Consequences**

* **Migration Timeline**: v2.0 represents significant architectural evolution requiring careful migration planning
* **Dependency Evolution**: May enable future upgrade of detection libraries (charset-normalizer)
* **Plugin Foundation**: Architecture provides foundation for future plugin system without committing to implementation

**Implementation Implications**

* Focus on context-driven detection logic that automatically selects appropriate methods
* Implement detector registry system with configurable backend precedence
* Design Behaviors dataclass for intuitive validation control and detector ordering
* Maintain strict backward compatibility through enhanced function implementations
* Create comprehensive test suite covering behavior combinations and context scenarios
* Document migration patterns for common integration scenarios

**Integration with Existing Architecture**

This decision supersedes the limitations identified in ADR-002 by providing 
a concrete v2.0 architecture that addresses real-world integration needs while 
maintaining the functional API paradigm established in ADR-001. The context-aware 
approach extends the faithful reproduction principle to include context utilization 
and configurable behaviors without breaking existing usage patterns.