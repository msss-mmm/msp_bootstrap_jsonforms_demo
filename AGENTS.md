# System Specification: Manufacturing Execution & Document Pipeline

For detailed technical implementation details, architecture, and behavioral requirements, refer to [DESIGN.md](./DESIGN.md).

## Overview
This document specifies the requirements for a Document Management System (DMS) designed to transition from paper-based workflows to a secure, multi-user digital platform. The system utilizes a dynamic, schema-driven approach to manage document templates and their resulting instances.

## Recommended Technology Stack
The system is designed to be technology-agnostic where possible, but the following stack is recommended for compatibility with the current implementation:
- **Backend:** Django (Python) with REST API support.
- **Frontend:** Vue 3 (Composition API) for a responsive single-page application.
- **UI Framework:** Element Plus for consistent interface components.
- **Dynamic Form Engine:** JSON Forms with a custom drag-and-drop builder for visual template authoring and runtime rendering.

## Document and Template Lifecycle
The system manages the lifecycle of form definitions (**Templates**) and their specific completions (**Document Instances**).

### Template Lifecycle
- **Active:** Available for selection when creating new document instances.
- **Inactive:** Hidden from the "New Document" creation menu but still associated with existing instances.
- **Archived:** Segregated from the main management view; templates in this state cannot be used for new documents. Templates can be restored to Active status from the archive.

### Document Instance Lifecycle
- **Active:** Fully editable and open for data entry.
- **Locked:** Transitioned to a read-only state to prevent further modification. Locked documents can be unlocked to return to an Active state.
- **Archived:** Removed from active lists and stored in a secondary archive view. Documents can be restored to Active status from the archive.

## User Interaction Logic
- **Privilege Management:** User actions and access levels are governed by configurable privileges. These privileges determine which roles can view, edit, lock, or archive specific documents and templates. System administrators are responsible for the configuration of these role-based permissions.
- **Workflow Approvals:** The system incorporates custom approval components (e.g., Operator and QA signatures). These components record the user identity and a timestamp directly into the document's data schema.
- **State-Based UI:** The user interface dynamically adjusts based on the status of the entity (e.g., disabling form fields or hiding action buttons for locked documents) and the current user's privileges.

## Document Editor
- **Low-Code Designer:** A visual, drag-and-drop interface allows for the creation of complex document templates using JSON Schema and UI Schema.
- **JSON Schema & UI Schema:** Template definitions follow the JSON Forms standard, with a data schema for structure and a UI schema for layout, enabling flexible data models and runtime form generation.
- **Storage Synchronization:** To ensure portability and ease of initialization, template definitions are synchronized between the primary database and a local filesystem directory (e.g., as `.json` files).

## Network & Security Constraints
- **Strict Local Access:** The application must be entirely self-contained. There must be no runtime client-side or server-side access to any hosts outside of the designated backend environment.
- **Local Asset Serving:** All dependencies, including scripts, styles, fonts, and icons, must be served from the application's own infrastructure. The use of Content Delivery Networks (CDNs) or external asset hosting is prohibited.
- **Telemetry & Tracking:** The system must not contain any tracking, telemetry, or analytics code that makes outbound requests to third-party services.
- **External API Restrictions:** Any features within third-party components that attempt to contact external APIs (e.g., AI-assisted design features, automatic updates, or cloud-based previews) must be explicitly disabled at the configuration level.
