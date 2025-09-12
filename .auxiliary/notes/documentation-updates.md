# Documentation Updates for v2.0

## README.rst Simple Examples

### 1. MIME Type and Charset Detection (Lines 98-116):
```python
import detextive

with open('document.txt', 'rb') as file:
    content = file.read()

# Individual detection
mimetype = detextive.detect_mimetype(content, location='document.txt')
charset = detextive.detect_charset(content)

# Combined inference
mimetype, charset = detextive.infer_mimetype_charset(
    content, location='document.txt')
print(f"Detected: {mimetype} with {charset} encoding")
```

### 2. Line Separator Processing (Lines 117-131):
*Keep as-is - this looks correct*

### 3. Content Classification (Lines 132-145):
```python
import detextive

# Check if MIME type represents textual content
detextive.is_textual_mimetype('application/json')  # True
detextive.is_textual_mimetype('image/jpeg')        # False

# Validate decoded text content
text = "Hello world!"
detextive.is_valid_text(text)      # True

# Invalid text with control characters
text_with_controls = "Hello\x00\x01world"
detextive.is_valid_text(text_with_controls)  # False
```

### 4. NEW: High-Level Decoding (add after Content Classification):
```python
import detextive

# High-level bytes-to-text decoding with validation
with open('document.txt', 'rb') as file:
    content = file.read()

# Decode with automatic charset detection and text validation
text = detextive.decode(content, location='document.txt')
print(f"Decoded text: {text}")
```

## Key Changes Made:
- Replace `detect_mimetype_and_charset()` → `infer_mimetype_charset()`
- Replace `is_textual_content()` → `is_valid_text()` 
- Add new `decode()` example
- Use `location` parameter instead of just filename
- Keep examples simple without confidence/behaviors complexity

## Notes:
- Confidence system should not be showcased in README (internal detail)
- More advanced examples will go in @documentation/examples/
- This is a new major release, no backward compatibility mentions needed

## Documentation Examples Structure

### Proposed Structure for documentation/examples/

#### **1. `basic-usage.rst`** (Core Detection)
- **Character Encoding Detection** (updated API)
- **MIME Type Detection** (updated API) 
- **High-Level Decoding** (new `decode()` function)
- **Content Validation** (updated to `is_valid_text()` and validation profiles)

#### **2. `advanced-configuration.rst`** (Advanced Configuration)
- **Custom Behaviors** (confidence thresholds, trial decode settings)
- **HTTP Content-Type Parsing** (new v2.0 feature)
- **Location-Based Inference** (enhanced context awareness)
- **Error Handling** (updated exception hierarchy)

#### **3. `line-separators.rst`** (keep focused)
- **Line Separator Detection** (unchanged - works well)
- **Line Ending Normalization** (unchanged - works well)

### Key Updates Needed:

**API Changes:**
- `detect_mimetype_and_charset()` → `infer_mimetype_charset()`
- `is_textual_content()` → `is_valid_text()`
- Add `decode()` examples
- Add `location` parameter usage
- Remove parameter overrides (doesn't exist in v2.0)

**New Sections to Add:**
- Text validation profiles (`PROFILE_TEXTUAL`, etc.)
- Confidence-aware detection (basic usage without exposing complexity)
- HTTP Content-Type parsing examples

**Structure Benefits:**
- **basic-usage.rst**: 80% of users will only need this
- **advanced-configuration.rst**: Power users and integration scenarios  
- **line-separators.rst**: Specialized but self-contained