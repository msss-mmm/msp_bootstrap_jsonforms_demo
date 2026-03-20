from django.test import TestCase, RequestFactory
from django.urls import reverse
from core.middleware import XForwardedPrefixMiddleware

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
