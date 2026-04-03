from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from core.models import Template, DocumentInstance
from unittest.mock import patch, MagicMock
import os

@override_settings(SKIP_JSON_SYNC=True)
class SavePDFTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.template = Template.objects.create(
            name="Test Template",
            schema={"type": "object"},
            status="Active"
        )
        self.document = DocumentInstance.objects.create(
            template=self.template,
            title="Test Document",
            data={},
            status="Active"
        )
        self.url = reverse('documentinstance-save-pdf', kwargs={'pk': self.document.pk})

    @patch('core.views.sync_playwright')
    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_save_pdf_uses_frontend_url_setting(self, mock_exists, mock_makedirs, mock_playwright):
        # Setup mocks
        mock_exists.return_value = False # Mock not in docker for this test

        # Mock Playwright context manager and browser
        mock_p = mock_playwright.return_value.__enter__.return_value
        mock_browser = mock_p.chromium.launch.return_value
        mock_page = mock_browser.new_page.return_value

        with override_settings(FRONTEND_URL='http://test-frontend:5000'):
            response = self.client.post(self.url)

        self.assertEqual(response.status_code, 200)

        # Verify that page.goto was called with the correct URL constructed from settings
        # The expected URL is: {FRONTEND_URL}/documents/{id}?user=Admin
        expected_url = f"http://test-frontend:5000/documents/{self.document.id}?user=Admin"
        mock_page.goto.assert_called_once_with(expected_url)

    @patch('core.views.sync_playwright')
    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_save_pdf_no_longer_accepts_base_url_from_client(self, mock_exists, mock_makedirs, mock_playwright):
        # Even if client sends base_url, it should be ignored in favor of settings
        mock_exists.return_value = False

        mock_p = mock_playwright.return_value.__enter__.return_value
        mock_browser = mock_p.chromium.launch.return_value
        mock_page = mock_browser.new_page.return_value

        with override_settings(FRONTEND_URL='http://configured-frontend'):
            # Send a different base_url in request
            response = self.client.post(self.url, {'base_url': 'http://malicious-site.com'}, format='json')

        self.assertEqual(response.status_code, 200)

        # Should still use configured-frontend
        expected_url = f"http://configured-frontend/documents/{self.document.id}?user=Admin"
        mock_page.goto.assert_called_once_with(expected_url)
