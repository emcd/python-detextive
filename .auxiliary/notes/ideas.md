# Future Ideas for Detextive

## Postprocessors for v2.1+

Text postprocessing features to enhance decoded content:

### **Line Separator Normalization**
- `normalize_line_separators(text, target='unix')` - Convert CRLF/CR to LF
- Integration with `lineseparators.py` existing functionality
- Options: 'unix' (\n), 'windows' (\r\n), 'mac' (\r), 'universal'

### **ANSI Sequence Filtering**
- `filter_ansi_sequences(text, mode='strip')` - Remove or escape ANSI codes
- Modes: 'strip' (remove), 'escape' (show as \x1b[31m), 'safe' (allow basic colors only)
- Regex-based detection of CSI/OSC sequences
- Integration with validation profiles (TERMINAL_SAFE, etc.)

### **Unicode Normalization**
- `normalize_unicode(text, form='NFC')` - Apply Unicode normalization
- Forms: NFC, NFD, NFKC, NFKD via unicodedata
- Useful for consistent text processing across platforms

### **Whitespace Standardization**
- `normalize_whitespace(text, preserve_breaks=True)` - Standardize spacing
- Convert tabs to spaces, collapse multiple spaces, trim lines
- Preserve paragraph breaks vs. full normalization modes

## Architecture Considerations

### **Plugin System**
- Registry-based postprocessor plugins
- Composable processing pipeline
- Built-in processors + user extensions

### **Integration Points**
- `decode(..., postprocessors=['normalize_lines', 'filter_ansi'])`
- Chained processing with error handling
- Performance: avoid re-encoding/decoding

### **Configuration**
- PostprocessorBehaviors DTO for settings
- Profile-based defaults (TERMINAL_SAFE auto-enables ANSI filtering)
- Per-processor configuration options

## Other Future Enhancements

### **Enhanced Detection**
- Machine learning confidence models
- Content-type specific heuristics

### **Caching**
- Content-based detection caching
- Confidence score persistence
- Performance optimization for repeated operations

### **Monitoring**
- Detection performance metrics
- Confidence score analytics
- Error pattern analysis
