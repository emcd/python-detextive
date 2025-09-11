ComparisonResult        # unused variable
NominativeArguments     # unused variable
PositionalArguments     # unused variable
package_name            # unused variable

# --- BEGIN: Injected by Copier ---
Omnierror              # unused base exception class for derivation
# --- END: Injected by Copier ---

# Refactor 2.0 - public API functions not yet exposed in __init__.py
detect_charset          # public API function
detect_mimetype         # public API function
infer_charset           # public API function
infer_mimetype_charset  # public API function
is_valid_text           # public API function

# Exception classes for public API
TextualMimetypeInvalidity  # exception class for public API

# LineSeparators enum methods - public API
detect_bytes            # LineSeparators class method
normalize_universal     # LineSeparators class method
normalize               # LineSeparators instance method
nativize                # LineSeparators instance method

# Function parameters - used in signatures
mimetype_default        # function parameter

# Validation profiles - public API constants
PROFILE_PRINTER_SAFE    # public validation profile
PROFILE_TERMINAL_SAFE   # public validation profile  
PROFILE_TERMINAL_SAFE_ANSI  # public validation profile

# Confidence system - planned for v2.0
DetectionResult         # confidence result dataclass
confidence              # DetectionResult field
detect_charset_candidates   # public API function for confidence-based detection
detect_mimetype_candidates  # public API function for confidence-based detection
text_validate_confidence # Behaviors field for confidence thresholds
trial_codecs            # Behaviors field (renamed from charset_trial_codecs)  
trial_decode_confidence # Behaviors field for confidence thresholds
