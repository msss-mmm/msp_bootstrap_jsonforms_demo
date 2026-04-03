# Technical Design Document

This document describes the current technical architecture, behaviors, and requirements of the DMS Document Pipeline project. It serves as a reference for understanding the system's present state and implementation details.

## 1. Architecture Overview

### Tech Stack
- **Frontend:** Vue 3 (Composition API), Element Plus UI Framework.
- **Form Engine:** [JSON Forms](https://jsonforms.io/) (fully migrated from legacy FormCreate).
- **Backend:** Django (Python 3.13+) with Django REST Framework and SQLite.
- **Infrastructure:** Docker & Docker Compose.
- **PDF Rendering:** Playwright (Chromium) for server-side generation; `window.print()` for client-side.

### Network & Environment
- **Air-gapped Design:** The system is self-contained with no external runtime dependencies or telemetry. All assets (fonts, icons, scripts) are served locally.
- **Reverse Proxy Support:** Supports deployment at subpaths (e.g., `/mes`) using `X-Forwarded-Prefix` and dynamic `BASE_URL` injection in the frontend.
- **Docker Networking:** Backend PDF rendering uses `http://ui` when running in Docker to bypass external proxies and internal networking complexities.

---

## 2. Frontend Architecture

### Layout & Styling
- **Viewport Management:** The application uses a non-scrolling, viewport-filling layout (`height: 100vh`) with `display: flex`. Global scrolling is disabled on the root container; child views manage internal scrolling via `overflow: auto`.
- **Edge Padding:** A consistent 40px edge padding convention is maintained (20px on `el-main` and 20px on the internal container).
- **Print Styling:** Custom `@media print` CSS ensures multi-page rendering by resetting flex containers to `display: block` and applying `page-break-inside: avoid` to layout items.

### Form Persistence & Interaction
- **Auto-save Mechanism:** `DocumentEdit.vue` employs an auto-save strategy. Text inputs are debounced (1s), while immediate actions (like Timer 'Start/Stop') trigger an instant save.
- **Navigation Protection:** SPA navigation is protected via `onBeforeRouteLeave`, and browser-level refreshes/back actions are caught by `window.onbeforeunload` when unsaved changes exist.
- **Locking Mechanism:** Locked documents maintain their interactive visual appearance but interaction is disabled using the HTML `inert` attribute on the form container.

---

## 3. Template Editor (JsonFormsBuilder.vue)

### Interface Design
- **3-Column Layout:** A fixed-height layout consisting of a Palette (left), Canvas (center), and Properties (right). Each column scrolls independently while the header remains static.
- **Canvas Interaction:**
    - Supports Vertical, Horizontal, and Group layouts.
    - Drag-and-drop positioning uses the Y-axis for Vertical/Group layouts and the X-axis for Horizontal layouts.
    - Empty layouts display a 100px high placeholder ("Drag Component Here").
    - Recursive stability is achieved by providing isolated `controlSchema` (leaf properties) to internal canvas elements to prevent infinite re-renders.

### Designer Logic
- **Nesting Validation:** Prevents invalid nesting (e.g., dragging a layout into itself or its descendants) by path comparison.
- **Infinite Loop Prevention:** Uses `isInternalUpdate` guards, `nextTick` resets, and deep JSON comparisons to synchronize canvas state with schema definitions.
- **Property Management:**
    - The properties panel dynamically adjusts based on field type.
    - Fields with enums (Radio, Multi-select) have a dedicated option manager.
    - Setting values on the canvas automatically activates the "Default Value" state in the sidebar.

---

## 4. Custom JSON Forms Renderers

### Implementation Principles
- **Rendering Pattern:** Renderers must use `:model-value` and explicit event handlers (e.g., `@change`) to call `onChange`. **Direct `v-model` on `control.data` is prohibited** as it causes UI freezes.
- **Ranking System:**
    - **100:** Timer, External Capture, Approval.
    - **25:** Choice-based (Radio, Multi-select).
    - **20:** Specialized primitives (Date, Time, Number, Boolean).
    - **10:** Generic String.
- **Read-Only Mode:** Standard renderers switch to `ReadOnlyField.vue` when `control.enabled` is false. Values are rendered as plain text (font-weight 700) with a dash `—` for empty values.

### Specialized Components
- **Timer:** Manages an object with `startTime`, `stopTime`, and `total`. Formats timestamps as `YYYY-MM-DD HH:mm:ss [TZ offset]` in Pacific Time and durations as `mm:ss`.
- **External Capture:** Polls a USGS water flow endpoint every 5 seconds for live visualization; captures a snapshot object (source, value, timestamp) upon user action.
- **Approval (Operator/QA):** Uses `ApprovalRenderer.vue`. Records identity and timestamp. Supports a `plainText` mode for read-only displays and print layouts.
- **Date/Time Pickers:** Configured to allow manual text entry (editable) with format hints (`YYYY:MM:DD`, `HH:MM:SS`) as placeholders.

---

## 5. Backend & Infrastructure

### Data Management
- **Persistence:** Templates and Documents are stored in SQLite.
- **Migrations & Seeding:**
    - `python manage.py migrate`: Standard database setup.
    - `python manage.py seed_data`: Populates the system with computer-themed example templates and documents.
- **Template Synchronization:** `python manage.py prime_templates` synchronizes the database with JSON files located in the `api/templates/` directory.

### PDF Generation
- **Server-Side Rendering:** Uses Playwright to render documents via the configured `FRONTEND_URL`.
- **Storage:** Generated PDFs are saved to `api/pdfs/` and are excluded from version control.
- **Sanitization:** Filenames are sanitized by removing non-alphanumeric characters and replacing spaces with underscores.
