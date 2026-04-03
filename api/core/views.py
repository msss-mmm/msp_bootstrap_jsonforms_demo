import os
import re
from playwright.sync_api import sync_playwright
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Template, DocumentInstance
from .serializers import TemplateSerializer, DocumentInstanceSerializer

class TemplateViewSet(viewsets.ModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer

class DocumentInstanceViewSet(viewsets.ModelViewSet):
    queryset = DocumentInstance.objects.all()
    serializer_class = DocumentInstanceSerializer

    @action(detail=True, methods=['post'])
    def save_pdf(self, request, pk=None):
        instance = self.get_object()

        # Security: The backend strictly uses the pre-configured FRONTEND_URL.
        # In Docker, this defaults to 'http://ui' to reach the frontend container.
        base_url = settings.FRONTEND_URL.rstrip('/')

        # Note: We append a mock user query param in case future auth needs it.
        # In current setup, the app is open-access for rendering.
        frontend_url = f"{base_url}/documents/{instance.id}?user=Admin"

        pdfs_dir = os.path.join(settings.BASE_DIR, 'pdfs')
        os.makedirs(pdfs_dir, exist_ok=True)

        # Sanitize title for filename
        sanitized_title = re.sub(r'[^\w\s-]', '', instance.title).strip().replace(' ', '_')
        pdf_filename = f"{sanitized_title}.pdf"
        pdf_path = os.path.join(pdfs_dir, pdf_filename)

        # PERFORMANCE NOTE: Launching a browser synchronously is heavy.
        # In production, this should be offloaded to a task queue (e.g. Celery).
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(args=["--no-sandbox"])
                page = browser.new_page()
                page.goto(frontend_url)
                page.emulate_media(media="print")
                # Wait for .document-edit as confirmed in source
                page.wait_for_selector(".document-edit", state="visible")
                # Ensure data and styles are loaded
                page.wait_for_load_state("networkidle")
                page.pdf(path=pdf_path)
                browser.close()

            return Response({"message": f"PDF saved as {pdf_filename}"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
