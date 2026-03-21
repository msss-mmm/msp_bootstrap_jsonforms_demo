from django.db import models

class Document(models.Model):
    TRAVELER = 'traveler'
    INSTRUCTIONS = 'instructions'
    DOC_TYPES = [
        (TRAVELER, 'Work Order Traveler'),
        (INSTRUCTIONS, 'Instructions'),
    ]

    doc_type = models.CharField(max_length=20, choices=DOC_TYPES)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.doc_type})"

class Traveler(models.Model):
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='traveler_details')
    work_order = models.CharField(max_length=100, blank=True)
    warehouse = models.CharField(max_length=100, blank=True)
    part_number = models.CharField(max_length=100, blank=True)
    quantity = models.IntegerField(default=1)
    serial_number = models.TextField(blank=True) # Multi-line S/N

class TravelerStep(models.Model):
    traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE, related_name='steps')
    step_number = models.IntegerField() # 10, 20, 30, 40, 50
    label = models.CharField(max_length=100) # step 1, step 2...

    operator_name = models.CharField(max_length=100, blank=True, null=True)
    operator_timestamp = models.DateTimeField(blank=True, null=True)

    qa_name = models.CharField(max_length=100, blank=True, null=True)
    qa_timestamp = models.DateTimeField(blank=True, null=True)

    notes = models.TextField(blank=True)

    # Fields for step 50
    operation = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        ordering = ['step_number']

class Instruction(models.Model):
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='instruction_details')
    part_number = models.CharField(max_length=100, blank=True)
    revision = models.CharField(max_length=50, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

class InstructionStep(models.Model):
    instruction = models.ForeignKey(Instruction, on_delete=models.CASCADE, related_name='steps')
    step_number = models.IntegerField() # Static increasing number
    instruction_text = models.TextField() # Text with placeholders like {{entry}}

    operator_name = models.CharField(max_length=100, blank=True, null=True)
    operator_timestamp = models.DateTimeField(blank=True, null=True)

    qa_name = models.CharField(max_length=100, blank=True, null=True)
    qa_timestamp = models.DateTimeField(blank=True, null=True)

    # JSON field to store the values of entries in instruction_text
    entry_values = models.JSONField(default=list)

    class Meta:
        ordering = ['step_number']
