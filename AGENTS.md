# AGENTS.md: Manufacturing Execution & Document Pipeline

## Overview
This document defines the **Digital Agents** (Backend Logic Layers) responsible for transitioning a legacy "paper and binder" workflow into a secure, multi-user digital system. These agents enforce the **Order of Operations**, manage **Role-Based Access Control (RBAC)**, and ensure data integrity across the manufacturing pipeline.

---

## 1. The Validator Agent (Data Integrity)
**Responsibility:** Enforces "Template Logic" and BOM compliance before any data is committed to the MySQL database.
* **Business Logic:** Compares real-time data entry (e.g., Mix Records) against the master BOM.
* **Constraint Engine:** Rejects submissions if values (weight, temperature, quantity) fall outside of defined tolerances.
* **Conditional Logic:** If a specific part is flagged as "Hazardous" in the template, this agent forces the display and acknowledgment of specific Safety SOPs.

## 2. The Gatekeeper Agent (Workflow & Sequential Approval)
**Responsibility:** Replicates the physical "Hand-Filled & Stamped" workflow in a digital sequence.
* **Order of Operations:** Prevents "Step 2" from being edited or viewed until "Step 1" has received a valid digital stamp.
* **The Digital Stamp:** Records a `User_ID`, `Timestamp`, and `Role_Snapshot` (Quality, Supply Chain, or Operator) for every approval.
* **Manager Intervention:** If a Manager (Quality or Supply Chain) rejects a step, this agent rolls the document status back to `REVISIONS_NEEDED` and locks forward progress.

## 3. The Traffic Controller (Multi-User Concurrency)
**Responsibility:** Manages dozens of simultaneous users to prevent data collisions and "Race Conditions."
* **Optimistic Locking:** Uses version tracking on all records. If two Managers attempt to approve the same Traveler simultaneously, the second save is rejected with a "Document has been updated by another user" alert.
* **Record Level Locking:** Implements MySQL `SELECT FOR UPDATE` during the "Stamping" process to ensure a single source of truth during high-traffic shifts.
* **Session Heartbeat:** Provides real-time "Read-Only" indicators in the Bootstrap UI if another user is currently editing a specific document.

## 4. The Hierarchy & Routing Agent (Reporting Structure)
**Responsibility:** Manages the organizational tree and document escalation.
* **Role Scoping:** * **Operators:** Access limited to "active" work orders and SOPs.
    * **Quality Managers:** Global view of "Pending Approval" queue and Mix Records.
    * **Supply Chain Managers:** Authority over BOMs and Customer Order links.
* **Automatic Routing:** Once an Operator completes a "Mix Record," this agent automatically pushes a notification to the assigned Quality Manager's dashboard.

## 5. The Relationship Agent (Relational Architecture)
**Responsibility:** Maintains the "One-to-Many" links between all system entities.
* **Traceability:** Ensures every unique Part ID can be traced back through its Traveler -> BOM -> Customer Order -> Project.
* **Auto-Linking:** When a new "Leg" of a project is created, this agent automatically clones the required SOPs and Mix Record templates into the new Traveler instance.

## 6. The Reporting & Audit Agent (Search & History)
**Responsibility:** Searchability and Compliance Exports.
* **The Digital Binder:** Compiles all steps, images, and stamps into a single, unalterable "Birth Certificate" (PDF/Report) for the finished part.
* **Global Search:** Indexes JSON content from templates to allow Managers to search by Part Number, Batch ID, or Customer Order across the entire history.
* **Audit Trail:** Maintains a "Shadow Table" of every change made to a document for ISO-9001 or similar quality audits.

## 7. The Interface Agent (Multi-Frontend Architecture)
**Responsibility:** Translates backend state into several user-facing frontends based on the specific manufacturing context.
* **HTMX (Server-Side Interactivity):** Default interface for fast, server-driven reactive components without full page reloads.
* **Vuetify (Client-Side Interactive):** High-density Vue-based UI for complex manager dashboards and project overviews.
* **Vanilla JS / Bootstrap (No-Framework):** Low-overhead interface for simple shop floor data entry on legacy hardware.
* **Schema-Driven UI (Vue + JSONForms):** Dynamically generates forms from JSON Schemas. This decouples HTML from data, allowing for complex layout definitions (Vertical/Horizontal/Group) and real-time validation without manual coding of form fields.

---

## 8. The Persistence Agent (JSON-Field Logic)
**Responsibility:** Manages the storage and retrieval of unstructured manufacturing data within the structured relational database.
* **Dynamic Data Entry:** Stores non-standardized values (measurements, weights, unique attributes) in a `JSONField` (e.g., `data_entry`).
* **Schema-to-UI Mapping:** Links a `data_definition` (JSON Schema) to a specific `UnitProcess`, ensuring the UI Agent knows exactly how to render and validate the input before it hits the database.
* **Debounced Persistence:** Implements "Save-as-you-type" logic to ensure data is synchronized with the backend in real-time during long-form data entry.

---

### Technical Stack Summary
* **Backend:** Python 3.13 (Django 6.0+)
* **Database:** MySQL 8.0+ (Leveraging native `JSON` column types)
* **Frontend Strategy:**
    * JSONForms (Custom Vue Renderer) for schema-driven form generation.
* **Concurrency:** Python-level Optimistic Locking + MySQL Transaction Isolation
  
