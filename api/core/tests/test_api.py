from django.test import TestCase, RequestFactory, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from core.middleware import XForwardedPrefixMiddleware
from core.models import Template, DocumentInstance

@override_settings(SKIP_JSON_SYNC=True)
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

@override_settings(SKIP_JSON_SYNC=True)
class ModelTests(TestCase):
    def setUp(self):
        self.template = Template.objects.create(
            name="Test Template",
            schema={"type": "object"},
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

@override_settings(SKIP_JSON_SYNC=True)
class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.template = Template.objects.create(
            name="Test Template",
            schema={"type": "object"},
            uischema={
                "type": "VerticalLayout",
                "elements": [
                    {"type": "Control", "scope": "#/properties/op_1", "options": {"type": "OperatorApprove"}},
                    {"type": "Control", "scope": "#/properties/qa_1", "options": {"type": "QAApprove"}},
                    {"type": "Control", "scope": "#/properties/input_1"}
                ]
            },
            status="Active"
        )
        self.document = DocumentInstance.objects.create(
            template=self.template,
            title="Test Document",
            data={},
            status="Active"
        )

    def test_get_templates(self):
        url = reverse('template-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Test Template")
        self.assertEqual(response.data[0]['document_count'], 1)

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
            "schema": {"type": "object"},
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

    def test_create_template_duplicate_name(self):
        url = reverse('template-list')
        data = {
            "name": "Test Template",
            "schema": {"type": "object"},
            "status": "Active"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('name', response.data)

    def test_create_document_duplicate_title(self):
        url = reverse('documentinstance-list')
        data = {
            "template": self.template.id,
            "title": "Test Document",
            "status": "Active"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.data)

    def test_approval_status(self):
        url = reverse('documentinstance-list')

        # Initial: None
        response = self.client.get(url)
        doc = response.data[0]
        self.assertEqual(doc['operator_status'], 'none')
        self.assertEqual(doc['qa_status'], 'none')

        # Partial Operator
        self.document.data = {'op_1': {'name': 'operator'}}
        self.document.save()
        response = self.client.get(url)
        doc = response.data[0]
        self.assertEqual(doc['operator_status'], 'full') # Only 1 op field, so 1/1 is full
        self.assertEqual(doc['qa_status'], 'none')

        # Complex template with multiple fields
        complex_template = Template.objects.create(
            name="Complex Template",
            schema={"type": "object"},
            uischema={
                "type": "VerticalLayout",
                "elements": [
                    {"type": "Control", "scope": "#/properties/op_1", "options": {"type": "OperatorApprove"}},
                    {"type": "Control", "scope": "#/properties/op_2", "options": {"type": "OperatorApprove"}},
                    {"type": "Control", "scope": "#/properties/qa_1", "options": {"type": "QAApprove"}}
                ]
            },
            status="Active"
        )
        complex_doc = DocumentInstance.objects.create(
            template=complex_template,
            title="Complex Doc",
            data={'op_1': {'name': 'operator'}},
            status="Active"
        )
        response = self.client.get(url)
        # Find complex doc
        doc = next(d for d in response.data if d['id'] == complex_doc.id)
        self.assertEqual(doc['operator_status'], 'partial')
        self.assertEqual(doc['qa_status'], 'none')

        # Full complex
        complex_doc.data = {
            'op_1': {'name': 'operator'},
            'op_2': {'name': 'operator'},
            'qa_1': {'name': 'qa'}
        }
        complex_doc.save()
        response = self.client.get(url)
        doc = next(d for d in response.data if d['id'] == complex_doc.id)
        self.assertEqual(doc['operator_status'], 'full')
        self.assertEqual(doc['qa_status'], 'full')
