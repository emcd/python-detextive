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
Advanced Configuration
*******************************************************************************

This section demonstrates advanced usage including custom behaviors, confidence
thresholds, HTTP Content-Type parsing, and comprehensive error handling.

Custom Behaviors
===============================================================================

Confidence Thresholds
-------------------------------------------------------------------------------

Control detection confidence requirements through custom behaviors:

.. code-block:: python

    import detextive
    from detextive.core import Behaviors
    
    # Create custom behavior configuration
    strict_behaviors = Behaviors( 
        charset_confidence_minimum = 80,
        mimetype_confidence_minimum = 90
    )
    
    content = b'Potentially ambiguous content'
    
    # Use strict confidence requirements
    result = detextive.detect_charset_confidence( 
        content, 
        behaviors = strict_behaviors 
    )
    
    if result.confidence >= 80:
        print( f"High-confidence charset: {result.value}" )
    else:
        print( "Insufficient confidence in charset detection" )

Trial Decode Configuration
-------------------------------------------------------------------------------

Configure how trial decoding validates detected charsets:

.. code-block:: python

    import detextive
    from detextive.core import Behaviors, BehaviorTristate
    
    # Always perform trial decodes for validation
    validation_behaviors = Behaviors( 
        trial_decode = BehaviorTristate.Always,
        trial_decode_quantity_maximum = 2048
    )
    
    content = b'Content to validate through decoding'
    
    charset = detextive.detect_charset( 
        content, 
        behaviors = validation_behaviors 
    )
    
    print( f"Validated charset: {charset}" )

HTTP Content-Type Parsing
===============================================================================

Content-Type Header Processing
-------------------------------------------------------------------------------

Parse HTTP Content-Type headers to extract MIME type and charset:

.. code-block:: python

    import detextive
    
    # Parse complete Content-Type header
    content_type = "application/json; charset=utf-8; boundary=something"
    
    result = detextive.parse_http_content_type( content_type )
    
    print( f"MIME type: {result.mimetype}" )
    print( f"Charset: {result.charset}" )
    print( f"Parameters: {result.parameters}" )

Integration with Detection
-------------------------------------------------------------------------------

Use parsed Content-Type information to guide detection:

.. code-block:: python

    import detextive
    
    content = b'{"message": "Hello"}'
    http_header = "application/json; charset=utf-8"
    
    # Let HTTP header inform detection
    mimetype, charset = detextive.infer_mimetype_charset( 
        content, 
        http_content_type = http_header 
    )
    
    print( f"Inferred: {mimetype} with {charset}" )

Location-Based Inference
===============================================================================

Enhanced Context Awareness
-------------------------------------------------------------------------------

Provide rich location context to improve detection accuracy:

.. code-block:: python

    import detextive
    from pathlib import Path
    
    content = b'Configuration data'
    
    # Use Path objects for precise location context
    location = Path( 'config/settings.yaml' )
    
    mimetype = detextive.detect_mimetype( content, location = location )
    print( f"Context-aware MIME type: {mimetype}" )

Default Value Handling
-------------------------------------------------------------------------------

Specify fallback values when detection confidence is insufficient:

.. code-block:: python

    import detextive
    
    ambiguous_content = b'...'  # Content that's hard to classify
    
    mimetype, charset = detextive.infer_mimetype_charset( 
        ambiguous_content,
        mimetype_default = 'text/plain',
        charset_default = 'utf-8'
    )
    
    print( f"Result (with defaults): {mimetype}, {charset}" )

Text Validation Profiles
===============================================================================

Validation Profile Selection
-------------------------------------------------------------------------------

Choose validation strictness based on your use case:

.. code-block:: python

    import detextive
    from detextive.validation import (
        PROFILE_TEXTUAL, 
        PROFILE_TERMINAL_SAFE, 
        PROFILE_PRINTER_SAFE
    )
    
    text = "Sample text with Unicode: ☆"
    
    # Different validation profiles
    print( detextive.is_valid_text( text, profile = PROFILE_TEXTUAL ) )
    print( detextive.is_valid_text( text, profile = PROFILE_TERMINAL_SAFE ) )
    print( detextive.is_valid_text( text, profile = PROFILE_PRINTER_SAFE ) )

Profile-Aware Decoding
-------------------------------------------------------------------------------

Apply validation profiles during high-level decoding:

.. code-block:: python

    import detextive
    from detextive.validation import PROFILE_TERMINAL_SAFE
    
    content = b'Text for terminal display'
    
    try:
        text = detextive.decode( 
            content, 
            profile = PROFILE_TERMINAL_SAFE 
        )
        print( f"Terminal-safe text: {text}" )
    except detextive.exceptions.ValidationInvalidity as exception:
        print( f"Text validation failed: {exception}" )

Error Handling
===============================================================================

Exception Hierarchy
-------------------------------------------------------------------------------

Handle specific error conditions with appropriate exception types:

.. code-block:: python

    import detextive
    from detextive.exceptions import (
        DetectionInvalidity,
        ValidationInvalidity,
        DecodingFailure
    )
    
    try:
        # Attempt high-level processing
        text = detextive.decode( malformed_content, location = 'data.txt' )
        
    except DetectionInvalidity as exception:
        print( f"Detection failed: {exception}" )
        
    except ValidationInvalidity as exception:
        print( f"Text validation failed: {exception}" )
        
    except DecodingFailure as exception:
        print( f"Decoding failed: {exception}" )
        
    except detextive.exceptions.Omnierror as exception:
        print( f"General detextive error: {exception}" )

Confidence-Based Error Handling
-------------------------------------------------------------------------------

Handle low-confidence results gracefully:

.. code-block:: python

    import detextive
    
    def robust_charset_detection( content, minimum_confidence = 70 ):
        ''' Detects charset with confidence requirements. '''
        
        result = detextive.detect_charset_confidence( content )
        
        if result.confidence >= minimum_confidence:
            return result.value
        else:
            # Fall back to conservative default
            return 'utf-8'
    
    content = b'Ambiguous content'
    charset = robust_charset_detection( content )
    
    print( f"Robust charset detection: {charset}" )

Integration Patterns
===============================================================================

Complete Processing Pipeline
-------------------------------------------------------------------------------

Combine multiple detection steps in a robust processing pipeline:

.. code-block:: python

    import detextive
    from detextive.core import Behaviors
    from detextive.validation import PROFILE_TEXTUAL
    
    def process_document( content, location = None, http_content_type = None ):
        ''' Processes document with comprehensive detection and validation. '''
        
        # Configure strict behaviors
        behaviors = Behaviors( 
            charset_confidence_minimum = 75,
            trial_decode = detextive.core.BehaviorTristate.AsNeeded
        )
        
        try:
            # Detect MIME type and charset
            mimetype, charset = detextive.infer_mimetype_charset( 
                content,
                behaviors = behaviors,
                location = location,
                http_content_type = http_content_type
            )
            
            # Validate MIME type is textual
            if not detextive.is_textual_mimetype( mimetype ):
                return None, f"Non-textual content: {mimetype}"
            
            # Decode with validation
            text = detextive.decode( 
                content,
                behaviors = behaviors,
                profile = PROFILE_TEXTUAL,
                location = location,
                http_content_type = http_content_type
            )
            
            return text, None
            
        except detextive.exceptions.Omnierror as exception:
            return None, f"Processing failed: {exception}"
    
    # Example usage
    content = b'{"message": "Hello, world!"}'
    text, error = process_document( content, location = 'data.json' )
    
    if text:
        print( f"Processed text: {text}" )
    else:
        print( f"Processing error: {error}" )