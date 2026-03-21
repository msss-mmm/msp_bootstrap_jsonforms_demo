# AGENTS.md: Manufacturing Execution & Document Pipeline (FormCreate Version)

## Overview
This document defines the **Digital Agents** responsible for transitioning a legacy "paper and binder" workflow into a secure, multi-user digital system. This version of the system uses **FormCreate** and **Element Plus** for a fully dynamic, schema-driven approach to document templates and instances.

---

## 1. The Template Architect (Dynamic Form Definitions)
**Responsibility:** Manages the definition of documents using FormCreate JSON rules.
*   **Low-Code Editor:** Provides a visual drag-and-drop designer for administrators to create document templates.
*   **Schema Storage:** Stores document definitions (rules and options) as JSON in the database, with automated backups to the filesystem.
*   **Version Control:** Ensures templates can be updated without breaking existing document instances.

## 2. The Workflow Agent (Custom Approvals & Logic)
**Responsibility:** Enforces manufacturing logic within dynamic forms.
*   **Digital Stamps:** Implements `OperatorApprove` and `QAApprove` custom FormCreate components.
*   **Approval Logic:** Records `user_name` and `timestamp` directly within the document instance's data JSON.
*   **Field Locking:** Can trigger the disabling of other form components once an approval is granted to ensure data integrity.

## 3. The Persistence Agent (JSON-Field Logic)
**Responsibility:** Manages the storage and retrieval of all document data within a structured relational database.
*   **Generic Instances:** All documents (Travelers, Instructions, etc.) are stored as `DocumentInstance` records.
*   **JSON Data:** Real-time data entry is stored in a single `JSONField` (e.g., `data`), allowing for maximum flexibility in form design.
*   **Template Sync:** Automatically synchronizes database templates with the `backend/templates/` directory for system portability and initialization.

## 4. The Interface Agent (Vue 3 + Element Plus)
**Responsibility:** Renders the dynamic forms and management UI.
*   **Element Plus:** Provides a modern, clean UI for all management and data-entry views.
*   **Dynamic Rendering:** Uses the FormCreate engine to turn JSON rules into interactive Vue 3 components at runtime.
*   **Subpath Portability:** Supports deployment at any URL subpath through runtime environment detection.

---

### Technical Stack Summary
*   **Backend:** Python 3.13 (Django 6.0+)
*   **Database:** SQLite (with JSON column support)
*   **Frontend Strategy:**
    *   **Vue 3** (Composition API)
    *   **Element Plus** UI Framework
    *   **FormCreate** + **FormCreate Designer** for dynamic form management.
