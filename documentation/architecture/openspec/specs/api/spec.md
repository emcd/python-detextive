# API

## Purpose
The API capability provides a consistent and configurable interface for accessing detection and validation functionalities. It ensures standardized error handling, return types, and extensibility through a detector registry.

## Requirements

### Requirement: Unified Interface
The system SHALL provide a unified interface for detection functions (charset, mimetype) using common behavior configuration objects.

Priority: High

#### Scenario: Use common configuration
- **WHEN** calling detection functions
- **THEN** they accept a common behavior object

### Requirement: Configurable Behaviors
The system SHALL allow users to configure behaviors such as failure handling (error vs default value) and validation strictness.

Priority: High

#### Scenario: Configure failure handling
- **WHEN** behavior is configured to return default on failure
- **THEN** no exception is raised when detection fails

### Requirement: Extensibility
The system SHALL support adding new detectors via a registry mechanism without modifying core code.

Priority: Medium

#### Scenario: Register new detector
- **WHEN** a new detector is registered
- **THEN** it is used in subsequent detection calls
