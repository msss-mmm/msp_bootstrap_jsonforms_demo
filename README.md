# DMS Document Pipeline

A modern, dynamic Document Management System (DMS) to transition legacy "paper and binder" workflows into a secure, digital environment. This system uses a schema-driven approach for document templates and instances, powered by **JSON Forms** and **Element Plus**.

## Overview

The application allows administrators to design complex manufacturing forms (Travelers, Instructions, etc.) using a drag-and-drop designer. These templates are then used to generate document instances for real-time data entry on the shop floor, complete with digital approvals and state management.

## Tech Stack

- **Backend:** Python 3.13+, Django 6.0+, Django REST Framework
- **Frontend:** Vue 3 (Composition API), Element Plus UI Framework, JSON Forms
- **Database:** SQLite (default)
- **Deployment:** Docker & Docker Compose

## Document Workflow & Lifecycle

### Templates
Templates define the structure and rules of a document.
- **Active:** The template is available for creating new document instances.
- **Inactive:** The template is hidden from the "New Document" menu but remains in the main list for reference.
- **Archived:** The template is moved to the "Archive" tab. It cannot be used for new documents until restored.

### Document Instances
Documents are instances of a template where data is recorded.
- **Active:** The document is open for data entry and editing.
- **Locked:** The document is in a read-only state. It can be viewed but not modified.
- **Archived:** The document is moved to the "Archive" tab.

### Approval Logic
- **Digital Stamps:** The system uses custom `OperatorApprove` and `QAApprove` components.
- **Sequential Approval:** Typically, an Operator must provide approval before a QA representative can sign off.
- **Field Integrity:** Granting an approval often locks the associated fields to ensure data integrity after sign-off.

### Archive & Restore
- Archived templates and documents are grouped in a dedicated **Archive** tab to keep the main workspace clean.
- The only available action for archived items is **Restore**, which returns them to the **Active** state.

## Installation & Setup

### Environment Configuration
The application uses environment variables for configuration.
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and adjust the settings as needed (e.g., ports, subpath, secret keys).

### Running with Docker (Recommended)
The easiest way to get the system running is using Docker Compose:
```bash
docker-compose up --build
```
This will start both the api and ui services.

### Manual Installation

#### API Setup
1. Navigate to the api directory:
   ```bash
   cd api
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run migrations and seed initial data:
   ```bash
   python manage.py migrate
   python manage.py seed_data
   ```
4. Start the development server:
   ```bash
   python manage.py runserver
   ```

#### UI Setup
1. Navigate to the ui directory:
   ```bash
   cd ui
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## Management Commands
- `python manage.py seed_data`: Populates the database with example computer-themed templates and documents.
- `python manage.py prime_templates`: Synchronizes the database with JSON template definitions found in `api/templates/`.
