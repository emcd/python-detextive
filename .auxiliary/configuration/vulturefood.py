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

# Internal functions - keep for potential future use
_is_probable_textual_content  # legacy heuristic function

# Function parameters - used in signatures
mimetype_default        # function parameter
