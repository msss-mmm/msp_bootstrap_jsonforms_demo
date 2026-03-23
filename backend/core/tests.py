from django.test import TestCase, RequestFactory
from django.urls import reverse
from rest_framework.test import APIClient
from core.middleware import XForwardedPrefixMiddleware
from core.models import Template, DocumentInstance

class MiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = XForwardedPrefixMiddleware(lambda r: None)

    def test_x_forwarded_prefix_middleware(self):
        # Request with X-Forwarded-Prefix
        request = self.factory.get('/api/documents/', HTTP_X_FORWARDED_PREFIX='/mes')
        self.middleware(request)
        self.assertEqual(request.environ['SCRIPT_NAME'], '/mes')
        # Since /api/documents/ does not start with /mes, path_info should remain the same
        self.assertEqual(request.path_info, '/api/documents/')

    def test_x_forwarded_prefix_middleware_with_prefix_in_path(self):
        # Request where path already includes the prefix (depending on proxy config)
        request = self.factory.get('/mes/api/documents/', HTTP_X_FORWARDED_PREFIX='/mes')
        self.middleware(request)
        self.assertEqual(request.environ['SCRIPT_NAME'], '/mes')
        self.assertEqual(request.path_info, '/api/documents/')

    def test_x_forwarded_prefix_middleware_deep_subpath(self):
        # Request with a deeper subpath
        request = self.factory.get('/api/documents/', HTTP_X_FORWARDED_PREFIX='/prod/mes')
        self.middleware(request)
        self.assertEqual(request.environ['SCRIPT_NAME'], '/prod/mes')
        self.assertEqual(request.path_info, '/api/documents/')

    def test_x_forwarded_prefix_middleware_no_prefix(self):
        # Request without X-Forwarded-Prefix
        request = self.factory.get('/api/documents/')
        self.middleware(request)
        self.assertEqual(request.environ.get('SCRIPT_NAME', ''), '')
        self.assertEqual(request.path_info, '/api/documents/')

class ModelTests(TestCase):
    def setUp(self):
        self.template = Template.objects.create(
            name="Test Template",
            rule={"rule": "test"},
            status="Active"
        )

    def test_template_creation(self):
        self.assertEqual(self.template.name, "Test Template")
        self.assertEqual(self.template.status, "Active")

    def test_template_status_transition(self):
        self.template.status = "Inactive"
        self.template.save()
        self.assertEqual(self.template.status, "Inactive")

        self.template.status = "Archived"
        self.template.save()
        self.assertEqual(self.template.status, "Archived")

    def test_document_instance_creation(self):
        doc = DocumentInstance.objects.create(
            template=self.template,
            title="Test Document",
            status="Active"
        )
        self.assertEqual(doc.title, "Test Document")
        self.assertEqual(doc.template, self.template)
        self.assertEqual(doc.status, "Active")

    def test_document_instance_status_transition(self):
        doc = DocumentInstance.objects.create(
            template=self.template,
            title="Test Document",
            status="Active"
        )
        doc.status = "Locked"
        doc.save()
        self.assertEqual(doc.status, "Locked")

        doc.status = "Archived"
        doc.save()
        self.assertEqual(doc.status, "Archived")

class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.template = Template.objects.create(
            name="Test Template",
            rule={"rule": "test"},
            status="Active"
        )
        self.document = DocumentInstance.objects.create(
            template=self.template,
            title="Test Document",
            status="Active"
        )

    def test_get_templates(self):
        url = reverse('template-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Test Template")

    def test_get_documents(self):
        url = reverse('documentinstance-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Test Document")

    def test_create_template(self):
        url = reverse('template-list')
        data = {
            "name": "New Template",
            "rule": {"rule": "new"},
            "status": "Active"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Template.objects.count(), 2)

    def test_create_document(self):
        url = reverse('documentinstance-list')
        data = {
            "template": self.template.id,
            "title": "New Document",
            "status": "Active"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(DocumentInstance.objects.count(), 2)
