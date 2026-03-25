import os
import shutil
import json
from django.core.management import call_command
from django.test import TestCase
from django.conf import settings
from core.models import Template, DocumentInstance

class ImportRegressionTest(TestCase):
    def setUp(self):
        # Create a dedicated temporary directory for testing
        self.test_root = os.path.join(settings.BASE_DIR, 'test_tmp')
        self.test_templates_dir = os.path.join(self.test_root, 'templates')
        self.test_documents_dir = os.path.join(self.test_root, 'documents')
        os.makedirs(self.test_templates_dir, exist_ok=True)
        os.makedirs(self.test_documents_dir, exist_ok=True)

        # Path to actual data directories to backup/restore if necessary
        # However, for a cleaner test, we should mock settings.BASE_DIR
        self.old_base_dir = settings.BASE_DIR
        settings.BASE_DIR = self.test_root

        # Copy sample data from test_data/
        self.src_test_data = os.path.join(self.old_base_dir, '..', 'test_data')

        # Note: import_templates and import_documents expect files in settings.BASE_DIR/templates and settings.BASE_DIR/documents
        shutil.copytree(os.path.join(self.src_test_data, 'templates'), self.test_templates_dir, dirs_exist_ok=True)
        shutil.copytree(os.path.join(self.src_test_data, 'documents'), self.test_documents_dir, dirs_exist_ok=True)

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

    def tearDown(self):
        # Restore settings.BASE_DIR
        settings.BASE_DIR = self.old_base_dir
        # Cleanup temporary test directory
        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root)
