import json
from django.core.management.base import BaseCommand
from core.models import Template, DocumentInstance

class Command(BaseCommand):
    help = 'Seed the database with initial computer-themed templates and documents'

    def handle(self, *args, **kwargs):
        # Clear existing
        DocumentInstance.objects.all().delete()
        Template.objects.all().delete()

        # 1. Create a Traveler Template
        traveler_rule = [
            {"type":"input", "field":"work_order", "title":"Work Order", "value":"WO-2024-001"},
            {"type":"input", "field":"part_number", "title":"Part Number", "value":"CB-X1-PRO"},
            {"type":"inputNumber", "field":"quantity", "title":"Quantity", "value":5},
            {"type":"OperatorApprove", "field":"op_app_10", "title":"Step 10: Circuit Board Install"},
            {"type":"QAApprove", "field":"qa_app_10", "title":"QA Step 10"},
            {"type":"input", "field":"notes_10", "title":"Notes Step 10", "value":"All screws tightened."},
            {"type":"OperatorApprove", "field":"op_app_20", "title":"Step 20: Power Supply Install"},
            {"type":"QAApprove", "field":"qa_app_20", "title":"QA Step 20"}
        ]

        traveler_template = Template.objects.create(
            name="Computer Assembly Traveler",
            description="Manufacturing traveler for computer assembly",
            rule=traveler_rule,
            options={"form":{"labelPosition":"top"}}
        )

        # Create an instance
        DocumentInstance.objects.create(
            template=traveler_template,
            title="Traveler SN-A100-01",
            data={
                "work_order": "WO-2024-001",
                "part_number": "CB-X1-PRO",
                "quantity": 5,
                "op_app_10": {"name": "Operator", "timestamp": "2024-03-21T10:00:00Z"},
                "qa_app_10": {"name": "QA", "timestamp": "2024-03-21T10:05:00Z"},
                "notes_10": "Circuit board installed correctly. All screws tightened."
            }
        )

        # 2. Create an Instructions Template
        instruction_rule = [
            {"type":"input", "field":"part_number", "title":"Part Number", "value":"GAMING-PC-01"},
            {"type":"input", "field":"revision", "title":"Revision", "value":"B"},
            {"type":"text", "title":"Step 1: Install the motherboard and secure with 9 screws."},
            {"type":"OperatorApprove", "field":"op_app_1", "title":"Operator Approval Step 1"},
            {"type":"QAApprove", "field":"qa_app_1", "title":"QA Approval Step 1"}
        ]

        instruction_template = Template.objects.create(
            name="Computer Assembly Instructions",
            description="Assembly instructions for Gaming PC",
            rule=instruction_rule,
            options={"form":{"labelPosition":"top"}}
        )

        # Create an instance
        DocumentInstance.objects.create(
            template=instruction_template,
            title="Instructions Batch-2024-01",
            data={
                "part_number": "GAMING-PC-01",
                "revision": "B",
                "op_app_1": {"name": "Operator", "timestamp": "2024-03-21T11:00:00Z"},
                "qa_app_1": {"name": "QA", "timestamp": "2024-03-21T11:10:00Z"}
            }
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded new FormCreate templates and documents'))
