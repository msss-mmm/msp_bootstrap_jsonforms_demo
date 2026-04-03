import os
import re
from playwright.sync_api import sync_playwright
from django.conf import settings
from django.db import transaction
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
    def claim_mixture_record(self, request, pk=None):
        instance = self.get_object()
        date_prefix = request.data.get('date_prefix')
        doc_type = request.data.get('document_type')
        field_id = request.data.get('field_id')
        current_data = request.data.get('data', {})

        if not all([date_prefix, doc_type, field_id]):
            return Response({"error": "date_prefix, document_type, and field_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Use select_for_update to avoid race conditions on supported databases
            instance = DocumentInstance.objects.select_for_update().get(pk=instance.pk)

            # If already assigned, return it
            if instance.data.get(field_id):
                return Response({"mrn": instance.data[field_id]})

            # Regex to match the MRN format: YYMMDD[letters]_mr
            pattern = re.compile(rf"^{re.escape(date_prefix)}([a-z]+)_mr$")

            # Find all documents that might have this MRN
            docs = DocumentInstance.objects.filter(data__icontains=doc_type).filter(data__icontains=date_prefix)

            existing_letters = []
            for d in docs:
                if not isinstance(d.data, dict):
                    continue
                if doc_type in d.data.values():
                    for val in d.data.values():
                        if isinstance(val, str):
                            match = pattern.match(val)
                            if match:
                                existing_letters.append(match.group(1))

            def letter_to_num(s):
                n = 0
                for char in s:
                    n = n * 26 + (ord(char) - ord('a') + 1)
                return n - 1

            def get_excel_sequence(n):
                res = ""
                while n >= 0:
                    res = chr(ord('a') + (n % 26)) + res
                    n = (n // 26) - 1
                return res

            if not existing_letters:
                nums = [-1]
            else:
                nums = [letter_to_num(l) for l in existing_letters]

            while True:
                next_letter = get_excel_sequence(max(nums) + 1)
                mrn = f"{date_prefix}{next_letter}_mr"
                # Check for collisions across all documents
                if not DocumentInstance.objects.filter(data__icontains=mrn).exclude(pk=instance.pk).exists():
                    break
                nums.append(max(nums) + 1)

            # Update and save the instance
            final_data = current_data if current_data else instance.data
            final_data[field_id] = mrn
            instance.data = final_data
            instance.save()

            return Response({"mrn": mrn})

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
