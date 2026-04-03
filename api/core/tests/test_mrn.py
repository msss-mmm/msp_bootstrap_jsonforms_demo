from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Template, DocumentInstance

class MixtureRecordTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.template = Template.objects.create(
            name="Test Template",
            schema={
                "type": "object",
                "properties": {
                    "doc_type": {"type": "string"},
                    "mrn": {"type": "string"}
                }
            },
            uischema={
                "type": "VerticalLayout",
                "elements": [
                    {"type": "Control", "scope": "#/properties/doc_type", "options": {"type": "DocumentType"}},
                    {"type": "Control", "scope": "#/properties/mrn", "options": {"type": "MixtureRecordNumber"}}
                ]
            }
        )
        self.doc = DocumentInstance.objects.create(
            template=self.template,
            title="Test Doc",
            data={}
        )

    def test_claim_mixture_record(self):
        url = reverse('documentinstance-claim-mixture-record', args=[self.doc.id])
        data = {
            "date_prefix": "260403",
            "document_type": "recipe",
            "field_id": "mrn",
            "data": {"doc_type": "recipe"}
        }

        # First claim
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['mrn'], "260403a_mr")

        self.doc.refresh_from_db()
        self.assertEqual(self.doc.data['mrn'], "260403a_mr")
        self.assertEqual(self.doc.data['doc_type'], "recipe")

        # Second document, same type and date
        doc2 = DocumentInstance.objects.create(template=self.template, title="Test Doc 2", data={})
        url2 = reverse('documentinstance-claim-mixture-record', args=[doc2.id])
        data2 = {
            "date_prefix": "260403",
            "document_type": "recipe",
            "field_id": "mrn",
            "data": {"doc_type": "recipe"}
        }
        response2 = self.client.post(url2, data2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['mrn'], "260403b_mr")

    def test_claim_mixture_record_sequence(self):
        # Create 26 documents to exhaust a-z
        for i in range(26):
            DocumentInstance.objects.create(
                template=self.template,
                title=f"Doc {i}",
                data={"doc_type": "recipe", "mrn": f"260403{chr(ord('a')+i)}_mr"}
            )

        doc_next = DocumentInstance.objects.create(template=self.template, title="Next Doc", data={})
        url = reverse('documentinstance-claim-mixture-record', args=[doc_next.id])
        data = {
            "date_prefix": "260403",
            "document_type": "recipe",
            "field_id": "mrn",
            "data": {"doc_type": "recipe"}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['mrn'], "260403aa_mr")
