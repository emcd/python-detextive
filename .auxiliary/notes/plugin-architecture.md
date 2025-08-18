# Plugin Architecture for Detextive (Future Consideration)

## Executive Summary

This document explores potential plugin architecture designs for Detextive to support custom detection backends, alternative algorithms, and domain-specific detection logic. The plugin system would allow users to extend detection capabilities without modifying core Detextive code, enabling specialized detection for proprietary formats, enhanced accuracy through alternative libraries, and domain-specific validation rules.

## Motivation for Plugin Architecture

### Current Limitations

**Fixed Detection Pipeline**: Current implementation uses hardcoded detection sequence (magic bytes → mimetypes fallback) with no ability to inject custom logic or alternative libraries.

**Limited Extensibility**: Organizations with proprietary file formats or specialized content types cannot extend detection without forking Detextive.

**Algorithm Lock-in**: Users cannot experiment with alternative detection libraries or custom heuristics without code changes.

### Use Cases for Plugins

**Alternative Magic Detection**: Replace `puremagic` with `python-magic` (libmagic bindings) for more comprehensive format support.

**Domain-Specific Formats**: Add detection for proprietary formats in enterprise environments (custom database dumps, internal serialization formats).

**Enhanced Charset Detection**: Replace `chardet` with `cchardet` or `charset-normalizer` for improved performance or accuracy.

**Custom Validation Rules**: Implement organization-specific content validation (security policies, data format requirements).

**Confidence Scoring**: Add sophisticated confidence calculation algorithms based on multiple detection sources.

**Machine Learning Detection**: Integrate trained models for content classification in specialized domains.

## Plugin Types and Responsibilities

### Detection Backend Plugins

Replace or augment core detection engines:

```python
@__.typx.Protocol
class MimetypeDetectionPlugin:
    ''' Plugin for MIME type detection from content. '''
    
    name: __.typx.Annotated[
        str, __.ddoc.Doc( "Unique plugin identifier." )
    ]
    priority: __.typx.Annotated[
        int, __.ddoc.Doc( "Execution priority (higher = earlier)." )
    ]
    
    def detect_mimetype(
        self, 
        content: Content,
        context: DetectionContext,
    ) -> __.typx.Annotated[
        __.Absential[ str ],
        __.ddoc.Doc( "Detected MIME type or absent if undetectable." )
    ]: ...
    
    def supports_content(
        self,
        content: Content,
        context: DetectionContext,
    ) -> __.typx.Annotated[
        bool,
        __.ddoc.Doc( "Whether plugin can analyze this content type." )
    ]: ...

@__.typx.Protocol  
class CharsetDetectionPlugin:
    ''' Plugin for character encoding detection. '''
    
    name: str
    priority: int
    
    def detect_charset(
        self,
        content: Content,
        context: DetectionContext,
    ) -> __.Absential[ str ]: ...
    
    def supports_content(
        self,
        content: Content, 
        context: DetectionContext,
    ) -> bool: ...
```

### Validation Plugins

Custom content validation logic:

```python
@__.typx.Protocol
class ValidationPlugin:
    ''' Plugin for custom content validation rules. '''
    
    name: str
    priority: int
    
    def validate_content(
        self,
        content: Content,
        mimetype: __.Absential[ str ],
        charset: __.Absential[ str ],
        context: DetectionContext,
    ) -> __.typx.Annotated[
        ValidationResult,
        __.ddoc.Doc( "Validation outcome with optional error details." )
    ]: ...
    
    def applies_to_mimetype(
        self,
        mimetype: __.Absential[ str ],
    ) -> bool: ...

class ValidationResult( __.immut.DataclassObject ):
    ''' Result of content validation. '''
    
    is_valid: __.typx.Annotated[
        bool, __.ddoc.Doc( "Whether content passes validation." )
    ]
    confidence: __.typx.Annotated[
        float, __.ddoc.Doc( "Validation confidence (0.0-1.0)." )
    ]
    error_message: __.typx.Annotated[
        __.Absential[ str ], __.ddoc.Doc( "Error details if validation fails." )
    ] = __.absent
    metadata: __.typx.Annotated[
        __.cabc.Mapping[ str, __.typx.Any ],
        __.ddoc.Doc( "Additional validation metadata." )
    ] = __.immut.Dictionary( )
```

### Context Enhancement Plugins

Enrich detection context with additional information:

```python
@__.typx.Protocol
class ContextPlugin:
    ''' Plugin for enhancing detection context. '''
    
    name: str
    priority: int
    
    def enhance_context(
        self,
        content: Content,
        location: __.Absential[ Location ],
        http_context: __.Absential[ HttpContext ],
        base_context: DetectionContext,
    ) -> __.typx.Annotated[
        DetectionContext,
        __.ddoc.Doc( "Enhanced context with additional metadata." )
    ]: ...

class DetectionContext( __.immut.DataclassObject ):
    ''' Extended context for plugin-aware detection. '''
    
    location: __.Absential[ Location ] = __.absent
    http_context: __.Absential[ HttpContext ] = __.absent
    content_hash: __.Absential[ str ] = __.absent
    file_size: __.Absential[ int ] = __.absent
    source_encoding: __.Absential[ str ] = __.absent
    metadata: __.cabc.Mapping[ str, __.typx.Any ] = __.immut.Dictionary( )
```

## Plugin Registration and Discovery

### Registration API

```python
class PluginRegistry:
    ''' Central registry for detection plugins. '''
    
    def register_mimetype_plugin(
        self,
        plugin: MimetypeDetectionPlugin,
    ) -> None:
        ''' Registers MIME type detection plugin. '''
    
    def register_charset_plugin(
        self,
        plugin: CharsetDetectionPlugin,
    ) -> None:
        ''' Registers charset detection plugin. '''
    
    def register_validation_plugin(
        self,
        plugin: ValidationPlugin,
    ) -> None:
        ''' Registers content validation plugin. '''
    
    def register_context_plugin(
        self,
        plugin: ContextPlugin,
    ) -> None:
        ''' Registers context enhancement plugin. '''
    
    def unregister_plugin(
        self,
        plugin_name: str,
    ) -> None:
        ''' Removes plugin by name. '''

# Global registry instance
plugin_registry = PluginRegistry( )

# Registration convenience functions
def register_mimetype_plugin( plugin: MimetypeDetectionPlugin ) -> None:
    ''' Registers MIME type detection plugin globally. '''
    plugin_registry.register_mimetype_plugin( plugin )

def register_charset_plugin( plugin: CharsetDetectionPlugin ) -> None:
    ''' Registers charset detection plugin globally. '''
    plugin_registry.register_charset_plugin( plugin )
```

### Plugin Discovery

```python
# Manual registration
register_mimetype_plugin( LibmagicPlugin( ) )
register_charset_plugin( CchardetPlugin( ) )

# Entry point discovery (setuptools)
def discover_plugins( ) -> None:
    ''' Discovers and registers plugins from entry points. '''
    for entry_point in __.pkg_resources.iter_entry_points( 'detextive.plugins' ):
        plugin = entry_point.load( )
        if isinstance( plugin, MimetypeDetectionPlugin ):
            register_mimetype_plugin( plugin )
        elif isinstance( plugin, CharsetDetectionPlugin ):
            register_charset_plugin( plugin )
        # ... other plugin types
```

## Example Plugin Implementations

### Libmagic Backend Plugin

```python
class LibmagicPlugin:
    ''' MIME type detection using python-magic (libmagic bindings). '''
    
    name = 'libmagic'
    priority = 100  # High priority
    
    def __init__( self ):
        try:
            import magic
            self._magic = magic.Magic( mime = True )
            self._available = True
        except ImportError:
            self._available = False
    
    def supports_content( self, content: Content, context: DetectionContext ) -> bool:
        return self._available and len( content ) > 0
    
    def detect_mimetype( self, content: Content, context: DetectionContext ) -> __.Absential[ str ]:
        if not self._available: return __.absent
        try:
            result = self._magic.from_buffer( content )
            return result if result != 'application/octet-stream' else __.absent
        except Exception:
            return __.absent
```

### Enhanced Charset Plugin

```python
class CharsetNormalizerPlugin:
    ''' Character encoding detection using charset-normalizer. '''
    
    name = 'charset-normalizer'
    priority = 90
    
    def __init__( self ):
        try:
            import charset_normalizer
            self._normalizer = charset_normalizer
            self._available = True
        except ImportError:
            self._available = False
    
    def supports_content( self, content: Content, context: DetectionContext ) -> bool:
        return self._available and len( content ) > 32  # Minimum for reliable detection
    
    def detect_charset( self, content: Content, context: DetectionContext ) -> __.Absential[ str ]:
        if not self._available: return __.absent
        try:
            result = self._normalizer.from_bytes( content ).best( )
            return result.encoding if result and result.encoding else __.absent
        except Exception:
            return __.absent
```

### Custom Validation Plugin

```python
class SecurityValidationPlugin:
    ''' Custom validation for security policies. '''
    
    name = 'security-validator'
    priority = 50
    
    def applies_to_mimetype( self, mimetype: __.Absential[ str ] ) -> bool:
        if __.is_absent( mimetype ): return False
        # Apply to all text and script types
        return mimetype.startswith( 'text/' ) or mimetype in {
            'application/javascript',
            'application/json',
            'application/xml',
        }
    
    def validate_content(
        self,
        content: Content,
        mimetype: __.Absential[ str ],
        charset: __.Absential[ str ],
        context: DetectionContext,
    ) -> ValidationResult:
        # Example: Check for suspicious patterns
        if b'<script' in content.lower( ):
            return ValidationResult(
                is_valid = False,
                confidence = 0.9,
                error_message = "Content contains script tags",
                metadata = __.immut.Dictionary( security_risk = 'script_injection' ),
            )
        
        return ValidationResult( is_valid = True, confidence = 0.8 )
```

## Plugin-Aware Detection Pipeline

### Modified Core Functions

```python
def detect_mimetype_charset_with_plugins(
    content: Content,
    location: __.Absential[ Location ] = __.absent, *,
    http_context: __.Absential[ HttpContext ] = __.absent,
    behaviors: __.Absential[ Behaviors ] = __.absent,
    error_class_provider: __.Absential[ ErrorClassProvider ] = __.absent,
    use_plugins: bool = True,
) -> tuple[ __.Absential[ str ], __.Absential[ str ] ]:
    ''' Enhanced detection with plugin support. '''
    
    if not use_plugins:
        # Fallback to built-in detection
        return _detect_mimetype_charset_builtin( content, location, http_context, behaviors )
    
    # Build enhanced context
    context = _build_detection_context( content, location, http_context )
    context = _enhance_context_with_plugins( content, location, http_context, context )
    
    # Run plugin-based detection
    mimetype = _detect_mimetype_with_plugins( content, context )
    charset = _detect_charset_with_plugins( content, context )
    
    # Run validation plugins
    validation_results = _validate_with_plugins( content, mimetype, charset, context )
    if not all( result.is_valid for result in validation_results ):
        # Handle validation failures based on error_class_provider
        pass
    
    return mimetype, charset
```

### Plugin Execution Strategy

```python
def _detect_mimetype_with_plugins( content: Content, context: DetectionContext ) -> __.Absential[ str ]:
    ''' Executes MIME type detection plugins by priority. '''
    
    plugins = plugin_registry.get_mimetype_plugins( )
    plugins.sort( key = lambda p: p.priority, reverse = True )  # High priority first
    
    for plugin in plugins:
        if not plugin.supports_content( content, context ):
            continue
        
        try:
            result = plugin.detect_mimetype( content, context )
            if not __.is_absent( result ):
                return result
        except Exception as exc:
            # Log plugin failure, continue to next plugin
            logger.warning( f"Plugin {plugin.name} failed: {exc}." )
    
    # Fallback to built-in detection
    return _detect_mimetype_builtin( content, context.location )
```

## Configuration and Management

### Plugin Configuration

```python
class PluginConfiguration( __.immut.DataclassObject ):
    ''' Configuration for plugin behavior. '''
    
    enabled_plugins: __.typx.Annotated[
        frozenset[ str ], __.ddoc.Doc( "Names of enabled plugins." )
    ] = frozenset( )
    disabled_plugins: __.typx.Annotated[
        frozenset[ str ], __.ddoc.Doc( "Names of disabled plugins." )
    ] = frozenset( )
    plugin_timeout: __.typx.Annotated[
        float, __.ddoc.Doc( "Maximum execution time per plugin (seconds)." )
    ] = 1.0
    fallback_on_failure: __.typx.Annotated[
        bool, __.ddoc.Doc( "Use built-in detection if all plugins fail." )
    ] = True

# Global configuration
plugin_config = PluginConfiguration( )

def configure_plugins( config: PluginConfiguration ) -> None:
    ''' Updates global plugin configuration. '''
    global plugin_config
    plugin_config = config
```

### Plugin Isolation and Safety

```python
def _execute_plugin_safely( plugin: __.typx.Any, method: str, *args, **kwargs ) -> __.typx.Any:
    ''' Executes plugin method with timeout and exception handling. '''
    
    if plugin.name in plugin_config.disabled_plugins:
        return __.absent
    
    try:
        with __.contextlib.timeout( plugin_config.plugin_timeout ):
            return getattr( plugin, method )( *args, **kwargs )
    except TimeoutError:
        logger.warning( f"Plugin {plugin.name}.{method} timed out." )
        return __.absent
    except Exception as exc:
        logger.warning( f"Plugin {plugin.name}.{method} failed: {exc}." )
        return __.absent
```

## Integration Considerations

### Backwards Compatibility

- Plugin system entirely optional - existing code works unchanged
- Default behavior identical to current implementation when no plugins registered
- `use_plugins=False` parameter disables plugin system entirely

### Performance Impact

- Plugin discovery happens at registration time, not per-detection
- Failed plugins are logged but don't stop detection pipeline
- Timeout protection prevents plugins from blocking detection
- Built-in detection always available as fallback

### Security Considerations

- Plugin code execution isolated with timeouts
- Plugin failures logged but don't expose internal errors
- Configuration allows disabling problematic plugins
- Plugin validation should verify expected interfaces

## Future Extensibility

### Additional Plugin Types

**Format-Specific Plugins**: Specialized detection for document formats (PDF, Office, images).

**Network-Aware Plugins**: Integration with external detection services or databases.

**Caching Plugins**: Content-based caching for expensive detection operations.

**Monitoring Plugins**: Performance metrics and detection analytics.

### Plugin Ecosystem

**Plugin Repository**: Central registry for community-developed plugins.

**Plugin Packaging**: Standard packaging format for easy distribution.

**Plugin Testing Framework**: Standardized testing utilities for plugin developers.

**Plugin Documentation**: Templates and examples for plugin development.

## Conclusion

A plugin architecture would significantly extend Detextive's capabilities while maintaining backwards compatibility and performance. The protocol-based design allows flexible plugin types, while the priority-based execution system ensures reliable fallback behavior.

Key benefits include:
- **Extensibility**: Custom detection logic without core code changes
- **Performance**: Alternative libraries can be benchmarked and selected
- **Specialization**: Domain-specific detection rules and formats
- **Community**: Ecosystem of community-developed detection plugins

However, this represents a significant architectural addition that should be carefully considered against the complexity cost and actual user demand for extensibility features.