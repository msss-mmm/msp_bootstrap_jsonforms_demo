import json
import os
from django.core.management.base import BaseCommand
from core.models import Document, Traveler, TravelerStep, Instruction, InstructionStep
from django.utils import timezone

class Command(BaseCommand):
    help = 'Seed the database with initial computer-themed documents'

    def handle(self, *args, **kwargs):
        # Clear existing
        Document.objects.all().delete()

        # 1. Create a Traveler document
        traveler_doc = Document.objects.create(
            doc_type=Document.TRAVELER,
            name="Work Order Traveler - Computer Build A-100"
        )
        traveler = Traveler.objects.create(
            document=traveler_doc,
            work_order="WO-2024-001",
            warehouse="Main Warehouse - Sector 7",
            part_number="CB-X1-PRO",
            quantity=5,
            serial_number="SN-A100-01\nSN-A100-02\nSN-A100-03\nSN-A100-04\nSN-A100-05"
        )

        traveler_steps = [
            (10, "Circuit Board Install"),
            (20, "Power Supply Install"),
            (30, "Chips & RAM Install"),
            (40, "Hard Drive & Case Finish"),
            (50, "Final Quality Check")
        ]

        for num, label in traveler_steps:
            step = TravelerStep.objects.create(
                traveler=traveler,
                step_number=num,
                label=label
            )
            # Pre-fill step 10 to show progress
            if num == 10:
                step.operator_name = "Operator"
                step.operator_timestamp = timezone.now()
                step.qa_name = "QA"
                step.qa_timestamp = timezone.now()
                step.notes = "Circuit board installed correctly. All screws tightened."
                step.save()
            elif num == 20:
                step.notes = "Waiting for power supply arrival."
                step.save()

        # 2. Create an Instructions document
        instruction_doc = Document.objects.create(
            doc_type=Document.INSTRUCTIONS,
            name="Assembly Instructions - Gaming PC"
        )
        instruction = Instruction.objects.create(
            document=instruction_doc,
            part_number="GAMING-PC-01",
            revision="B",
            serial_number="VARIOUS",
            description="High-end gaming PC assembly with liquid cooling."
        )

        instruction_steps = [
            (1, "Install the motherboard and secure with {{entry}} screws.", ["9"]),
            (2, "Mount the power supply. Connect the main {{entry}} pin power cable.", ["24"]),
            (3, "Insert {{entry}} sticks of RAM into the slots.", ["4"]),
            (4, "Apply thermal paste and mount the CPU cooler. Verify temp is {{entry}} C.", ["35"])
        ]

        for num, text, entries in instruction_steps:
            step = InstructionStep.objects.create(
                instruction=instruction,
                step_number=num,
                instruction_text=text,
                entry_values=entries
            )
            # Pre-fill step 1
            if num == 1:
                step.operator_name = "Operator"
                step.operator_timestamp = timezone.now()
                step.qa_name = "QA"
                step.qa_timestamp = timezone.now()
                step.save()

        self.stdout.write(self.style.SUCCESS('Successfully seeded computer-themed documents'))
