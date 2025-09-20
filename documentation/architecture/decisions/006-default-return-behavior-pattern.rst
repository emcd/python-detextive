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
006. Default Return Behavior Pattern
*******************************************************************************

Status
===============================================================================

Accepted

Context
===============================================================================

The v2.0 architecture established in ADR-003 and ADR-005 implemented
sophisticated detection and validation behaviors but retained the v1.x
exception-based error handling for detection failures. Real-world integration
analysis revealed that **detection failure exceptions** create significant
integration friction for several use cases:

**Performance-Critical Pipelines**: Exception handling overhead degrades
performance in batch processing scenarios where detection failures are
common and expected.

**Defensive Programming Patterns**: Downstream packages implement extensive
try-catch blocks to handle detection failures, leading to verbose error
handling code.

**Fallback Value Workflows**: Many integrations require fallback to default
values (e.g., 'utf-8', 'application/octet-stream') when detection fails,
making exceptions inappropriate for expected failure scenarios.

**Graceful Degradation Requirements**: Content processing pipelines should
continue operating with reasonable defaults rather than failing completely
on detection uncertainty.

**Current Limitations:**

* Detection failures always raise exceptions, forcing defensive exception handling
* No mechanism to specify fallback values for failed detection attempts
* Binary success/failure model inappropriate for confidence-based detection
* Exception semantics inappropriate for expected failure scenarios (low-confidence content)

**Integration Pain Points:**

* Extensive try-catch blocks required for every detection call
* Custom fallback logic duplicated across downstream packages
* Performance overhead from exception handling in expected failure scenarios
* Inconsistent fallback value selection across different integrations

Decision
===============================================================================

We will implement a **Default Return Behavior Pattern** that provides
configurable failure handling through default value returns as an alternative
to exception-based error handling.

**Core Design Principles:**

**Configurable Failure Handling:**
* ``DetectFailureActions`` enum controls failure response strategy
* ``DetectFailureActions.Default`` returns configurable default values with zero confidence
* ``DetectFailureActions.Error`` preserves existing exception-based behavior
* Per-detection-type configuration via ``Behaviors.charset_on_detect_failure`` and ``mimetype_on_detect_failure``

**Default Value Parameters:**
* All detection functions accept optional ``default`` parameters
* System-wide defaults: ``CHARSET_DEFAULT = 'utf-8'`` and ``MIMETYPE_DEFAULT = 'application/octet-stream'``
* Default values returned with ``confidence = 0.0`` to indicate detection failure
* Consistent fallback behavior across all detection functions

**Backward Compatibility Strategy:**
* Default behavior configuration preserves existing exception semantics
* ``DetectFailureActions.Error`` maintains v1.x/v2.0 compatibility
* Optional ``default`` parameters enable opt-in default return behavior
* No breaking changes to existing function signatures or behavior

**Enhanced Function Interfaces:**

.. code-block:: python

    def detect_charset_confidence(
        content: Content, /, *,
        behaviors: Behaviors = BEHAVIORS_DEFAULT,
        default: str = CHARSET_DEFAULT,
        # ... other parameters
    ) -> CharsetResult:

    def detect_mimetype_confidence(
        content: Content, /, *,
        behaviors: Behaviors = BEHAVIORS_DEFAULT,
        default: str = MIMETYPE_DEFAULT,
        # ... other parameters
    ) -> MimetypeResult:

**Behaviors Configuration Integration:**

.. code-block:: python

    @dataclass
    class Behaviors:
        charset_on_detect_failure: DetectFailureActions = DetectFailureActions.Default
        mimetype_on_detect_failure: DetectFailureActions = DetectFailureActions.Default
        # ... existing fields

**Usage Patterns:**

.. code-block:: python

    # Default return behavior (new pattern)
    result = detect_charset_confidence(content)
    if result.confidence > 0.0:
        # Use detected charset
        charset = result.charset
    else:
        # Handle fallback case with returned default
        charset = result.charset  # 'utf-8'

    # Exception behavior (preserved pattern)
    behaviors = Behaviors(charset_on_detect_failure=DetectFailureActions.Error)
    try:
        result = detect_charset_confidence(content, behaviors=behaviors)
    except CharsetDetectFailure:
        # Handle detection failure explicitly

Alternatives
===============================================================================

**Optional Return Pattern with None Values**

*Benefits*: Explicit failure indication through None returns
*Drawbacks*: Breaking change to existing result types, None handling burden
*Rejection Reason*: Changes fundamental result contracts, breaks backward compatibility

**Result Union Types with Failure Variants**

*Benefits*: Type-safe failure handling, explicit success/failure distinction
*Drawbacks*: Complex type signatures, significant API surface changes
*Rejection Reason*: Over-engineering for failure handling, typing complexity burden

**Global Default Configuration**

*Benefits*: One-time configuration affects all detection calls
*Drawbacks*: Global state, less flexible per-call control, testing complexity
*Rejection Reason*: Conflicts with functional approach, reduces call-site flexibility

**Callback-Based Failure Handling**

*Benefits*: Maximum flexibility, custom failure logic per call
*Drawbacks*: Callback complexity, unclear control flow, testing burden
*Rejection Reason*: Over-engineering for common default value use case

**Dual Function APIs (detect vs try_detect)**

*Benefits*: Clear semantic distinction between failure modes
*Drawbacks*: API proliferation, maintenance burden, naming confusion
*Rejection Reason*: Violates API consolidation goal, creates duplicate functionality

Consequences
===============================================================================

**Positive Consequences**

* **Performance Optimization**: Eliminates exception handling overhead for expected failure scenarios
* **Integration Simplification**: Reduces defensive exception handling code in downstream packages
* **Graceful Degradation**: Enables content processing pipelines to continue with reasonable defaults
* **Backward Compatibility**: Preserves existing exception behavior through configuration
* **Consistent Fallbacks**: Standardizes default value selection across all integrations
* **Confidence-Based Decisions**: Zero confidence clearly indicates detection failure vs low-confidence detection

**Negative Consequences**

* **API Complexity**: Additional parameters and configuration options increase cognitive load
* **Failure Mode Confusion**: Two different failure handling patterns may confuse developers
* **Testing Matrix**: Failure action combinations expand test coverage requirements
* **Silent Failure Risk**: Default return behavior may mask legitimate detection problems

**Neutral Consequences**

* **Migration Strategy**: Opt-in nature allows gradual adoption of default return pattern
* **Error Handling Evolution**: Represents natural evolution from rigid exception model
* **Configuration Consistency**: Aligns with Behaviors pattern established in ADR-005

**Implementation Implications**

**Default Value Management:**
* Centralized default constants for consistency across functions
* Default parameters with reasonable fallback values for all detection types
* System-wide defaults align with common integration expectations

**Confidence Scoring Integration:**
* Zero confidence indicates detection failure vs uncertain detection
* Confidence thresholds enable AsNeeded behavior with default fallbacks
* Clear distinction between failed detection and low-confidence detection

**Charset Normalization Enhancement:**
* Centralized charset normalization through ``codecs.lookup()`` for consistency
* Handles charset name variations and aliases systematically
* Improves detection accuracy and reduces integration brittleness

**Configuration Evolution:**
* ``DetectFailureActions`` enum provides clear failure handling semantics
* Per-detection-type configuration enables granular failure handling control
* Maintains integration with existing BehaviorTristate patterns

**Migration Guidance:**

**Performance-Critical Integrations:**

.. code-block:: python

    # Enable default returns for batch processing
    behaviors = Behaviors(
        charset_on_detect_failure=DetectFailureActions.Default,
        mimetype_on_detect_failure=DetectFailureActions.Default,
    )

**Security-Conscious Integrations:**

.. code-block:: python

    # Preserve exception behavior for security validation
    behaviors = Behaviors(
        charset_on_detect_failure=DetectFailureActions.Error,
        mimetype_on_detect_failure=DetectFailureActions.Error,
    )

This decision addresses the exception handling limitations identified in
real-world integrations while maintaining the configurable behavior patterns
established in ADR-005. The default return pattern provides a foundation for
graceful degradation in confidence-based detection scenarios without breaking
existing exception-based integration patterns.