import os
import shutil
import json
import tempfile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.conf import settings
from core.models import Template, DocumentInstance

class ImportRegressionTest(TestCase):
    def setUp(self):
        # Create a dedicated temporary directory for testing
        self.test_root = tempfile.mkdtemp()
        self.test_templates_dir = os.path.join(self.test_root, 'templates')
        self.test_documents_dir = os.path.join(self.test_root, 'documents')
        os.makedirs(self.test_templates_dir, exist_ok=True)
        os.makedirs(self.test_documents_dir, exist_ok=True)

        # Use override_settings in a context manager for the duration of each test
        self.settings_override = override_settings(
            BASE_DIR=self.test_root,
            SKIP_JSON_SYNC=True
        )
        self.settings_override.enable()

        # Path to actual data directories
        # We need the real BASE_DIR to find the test data
        real_base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.src_test_data = os.path.join(real_base_dir, 'core', 'tests', 'test_data')

        # Note: import_templates and import_documents expect files in settings.BASE_DIR/templates and settings.BASE_DIR/documents
        # Copying templates to temporary test directory
        src_templates = os.path.join(self.src_test_data, 'templates')
        if os.path.exists(src_templates):
            for item in os.listdir(src_templates):
                s = os.path.join(src_templates, item)
                d = os.path.join(self.test_templates_dir, item)
                if os.path.isfile(s):
                    shutil.copy2(s, d)

        # Copying documents to temporary test directory
        src_documents = os.path.join(self.src_test_data, 'documents')
        if os.path.exists(src_documents):
            for item in os.listdir(src_documents):
                s = os.path.join(src_documents, item)
                d = os.path.join(self.test_documents_dir, item)
                if os.path.isfile(s):
                    shutil.copy2(s, d)

    def test_import_regression_data(self):
        # 1. Run import_templates
        call_command('import_templates')

        # Verify template created from test_data
        template = Template.objects.get(name="Regression Test Template")
        self.assertEqual(template.status, "Active")

        # 2. Run import_documents
        call_command('import_documents')

        # Verify document created from test_data
        doc = DocumentInstance.objects.get(title="Regression Test Document")
        self.assertEqual(doc.template.name, "Regression Test Template")
        self.assertEqual(doc.data["test_field"], "Sample Data")

    def test_import_document_without_template_fails(self):
        # Setup Document with non-existent template in the test directory
        document_data = {
            "template_name": "Missing Template",
            "title": "Orphan Document",
            "data": {},
            "status": "Active"
        }
        document_path = os.path.join(self.test_documents_dir, "orphan_document.json")
        with open(document_path, 'w') as f:
            json.dump(document_data, f)

        # Run import_documents
        call_command('import_documents')

        # Verify document NOT created
        with self.assertRaises(DocumentInstance.DoesNotExist):
            DocumentInstance.objects.get(title="Orphan Document")

    def test_import_template_update_on_collision(self):
        # Create template with same name but different description
        Template.objects.create(name="Regression Test Template", description="Original", schema={})

        call_command('import_templates')

        template = Template.objects.get(name="Regression Test Template")
        # Check if it was updated (assuming the one in test_data has a different description or just checking it didn't crash)
        self.assertEqual(template.status, "Active")

    def test_import_document_update_on_id_collision(self):
        # Clear existing document files in test_documents_dir
        for f in os.listdir(self.test_documents_dir):
            os.remove(os.path.join(self.test_documents_dir, f))

        # 1. Import templates first
        call_command('import_templates')
        template = Template.objects.get(name="Regression Test Template")

        # Remove existing documents in DB to avoid interference
        DocumentInstance.objects.all().delete()

        # 2. Create document with specific ID
        DocumentInstance.objects.create(id=999, template=template, title="Original Title", data={})

        # 3. Prepare JSON with same ID but different title
        document_data = {
            "id": 999,
            "template_name": "Regression Test Template",
            "title": "Updated Title",
            "data": {"foo": "bar"},
            "status": "Active"
        }
        document_path = os.path.join(self.test_documents_dir, "id_collision.json")
        with open(document_path, 'w') as f:
            json.dump(document_data, f)

        call_command('import_documents')

        doc = DocumentInstance.objects.get(id=999)
        self.assertEqual(doc.title, "Updated Title")

    def test_import_document_fail_on_title_collision_different_id(self):
        # Clear existing document files in test_documents_dir
        for f in os.listdir(self.test_documents_dir):
            os.remove(os.path.join(self.test_documents_dir, f))

        # 1. Import templates first
        call_command('import_templates')
        template = Template.objects.get(name="Regression Test Template")

        # Remove existing documents in DB to avoid interference
        DocumentInstance.objects.all().delete()

        # 2. Create document with a title
        DocumentInstance.objects.create(id=100, template=template, title="Collision Title", data={})

        # 3. Prepare JSON with same title but different (or no) ID
        document_data = {
            "id": 101,
            "template_name": "Regression Test Template",
            "title": "Collision Title",
            "data": {"foo": "bar"},
            "status": "Active"
        }
        document_path = os.path.join(self.test_documents_dir, "title_collision.json")
        with open(document_path, 'w') as f:
            json.dump(document_data, f)

        # This should fail/log error for this specific file, but not crash the command
        call_command('import_documents')

        # Verify the original document still exists and is unchanged
        doc = DocumentInstance.objects.get(id=100)
        self.assertEqual(doc.title, "Collision Title")
        self.assertEqual(doc.data, {})

        # Verify the new one was NOT created
        with self.assertRaises(DocumentInstance.DoesNotExist):
            DocumentInstance.objects.get(id=101)

    def tearDown(self):
        # Restore settings
        self.settings_override.disable()
        # Cleanup temporary test directory
        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root)
