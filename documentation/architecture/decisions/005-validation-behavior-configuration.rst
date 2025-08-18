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
005. Validation Behavior Configuration
*******************************************************************************

Status
===============================================================================

Accepted

Context
===============================================================================

The v1.x functional approach provides no control over validation execution, 
leading to inappropriate validation overhead and inflexible error handling 
for different use cases. Analysis of integration patterns revealed that 
validation requirements vary significantly based on context:

**Performance-Critical Scenarios**: Quick charset detection for decoding 
workflows should skip expensive printable character analysis.

**Security-Sensitive Contexts**: Comprehensive validation including trial 
decoding and character analysis required to prevent processing of 
malicious content.

**Batch Processing Workflows**: Different validation thresholds appropriate 
for automated processing versus interactive validation.

**Current Limitations:**

* All validation logic hardcoded with no runtime configuration
* No ability to skip expensive validations for performance-critical paths
* Fixed printable character thresholds inappropriate for all content types
* Trial decoding always performed regardless of use case requirements

**Requirements Analysis:**

* **Selective Validation**: Control which validation steps execute
* **Configurable Thresholds**: Adjust validation parameters for different content types
* **Performance Control**: Skip expensive operations when not required
* **Default Behavior**: Zero-configuration defaults for common use cases
* **Backward Compatibility**: Existing behavior preserved as default

Decision
===============================================================================

We will implement a **Behaviors Configuration Pattern** that provides 
fine-grained control over validation execution through a structured 
configuration object.

**Core Configuration Design:**

.. code-block:: python

    TriState: TypeAlias = Literal['never', 'as-needed', 'always']

    class Behaviors(DataclassObject):
        # Validation controls
        trial_decode: TriState = 'as-needed'
        validate_printable: TriState = 'as-needed'
        
        # Character validation
        printable_threshold: float = 0.0
        
        # Fallback behavior  
        assume_utf8_superset: bool = True

**TriState Validation Control:**

* **'never'**: Skip validation entirely for maximum performance
* **'as-needed'**: Apply validation based on detection confidence and context (default)
* **'always'**: Force validation regardless of confidence or context

**Threshold Configuration:**

* **printable_threshold**: Maximum fraction of non-printable characters allowed (0.0-1.0)
* Enables adjustment for different content types (code vs. prose vs. data)

**UTF-8 Handling:**

* **assume_utf8_superset**: Controls ASCII→UTF-8 promotion and suspected UTF-8 correction
* Addresses MacRoman false positive issues from chardet

**Integration Pattern:**

.. code-block:: python

    def detect_mimetype_charset(
        content: Content,
        location: Absential[Location] = absent, *,
        behaviors: Absential[Behaviors] = absent,
        # ... other parameters
    ) -> tuple[Absential[str], Absential[str]]:

**Default Behavior Design:**

.. code-block:: python

    BEHAVIORS_DEFAULT = Behaviors(
        trial_decode='as-needed',
        validate_printable='as-needed', 
        printable_threshold=0.0,
        assume_utf8_superset=True,
    )

Alternatives
===============================================================================

**Individual Boolean Parameters**

*Benefits*: Simple parameter interface, clear enable/disable semantics
*Drawbacks*: Parameter proliferation, no structured configuration
*Rejection Reason*: Leads to unwieldy function signatures as validation options grow

**Global Configuration Object**

*Benefits*: One-time configuration affects all function calls
*Drawbacks*: Global state, less flexible per-call control, testing complexity
*Rejection Reason*: Global state conflicts with functional approach

**Validation Profile Enums**

*Benefits*: Simple selection between predefined validation sets
*Drawbacks*: Limited flexibility, configuration coupling
*Rejection Reason*: Insufficient granularity for diverse use case requirements

**Builder Pattern Configuration**

*Benefits*: Fluent interface, incremental configuration building
*Drawbacks*: Over-engineering for configuration object, additional complexity
*Rejection Reason*: Functional configuration object simpler and more maintainable

Consequences
===============================================================================

**Positive Consequences**

* **Performance Control**: Skip expensive validations for performance-critical workflows
* **Use Case Flexibility**: Appropriate validation for security, performance, or accuracy requirements
* **Threshold Configurability**: Adjust validation parameters for different content types
* **Default Behavior**: Zero-configuration operation for common use cases
* **Structured Configuration**: Clear configuration object with documented semantics

**Negative Consequences**

* **Configuration Complexity**: Additional parameter and configuration object increase cognitive load
* **Testing Matrix**: Behavior combinations create large test space requiring systematic coverage
* **Documentation Overhead**: Configuration options require comprehensive documentation and examples
* **Implementation Complexity**: Conditional validation logic increases internal implementation complexity

**Neutral Consequences**

* **Migration Strategy**: Existing code continues working with default behaviors
* **Future Extensibility**: Configuration pattern provides foundation for additional validation options
* **Performance Characteristics**: Behavior selection affects performance profiles predictably

**Implementation Guidance**

**Performance-Optimized Configuration:**

.. code-block:: python

    # Quick charset detection for decoding
    fast_behaviors = Behaviors(
        trial_decode='never',
        validate_printable='never',
    )

**Security-Focused Configuration:**

.. code-block:: python

    # Comprehensive validation for untrusted content
    secure_behaviors = Behaviors(
        trial_decode='always',
        validate_printable='always',
        printable_threshold=0.05,  # Allow 5% non-printable
    )

**Content-Specific Configuration:**

.. code-block:: python

    # Relaxed validation for code/data content
    code_behaviors = Behaviors(
        printable_threshold=0.15,  # Allow more control characters
        validate_printable='as-needed',
    )

**Conditional Logic Implementation:**

Internal implementation will evaluate behavior configuration to determine 
which validation steps to execute, maintaining performance characteristics 
appropriate for each configuration profile.

**Integration with Error Class Provider:**

Behaviors configuration works in conjunction with error class provider pattern 
to provide complete control over validation execution and error handling:

.. code-block:: python

    result = detect_mimetype_charset(
        content, location,
        behaviors=secure_behaviors,
        error_class_provider=security_error_mapper,
    )

This decision provides the foundation for performance-aware and context-sensitive 
validation that addresses the rigid validation limitations of the v1.x functional 
approach while maintaining backward compatibility through sensible defaults.