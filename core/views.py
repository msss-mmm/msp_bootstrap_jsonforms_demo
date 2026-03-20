from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Document, Traveler, TravelerStep, Instruction, InstructionStep
from .serializers import DocumentSerializer, TravelerSerializer, TravelerStepSerializer, InstructionSerializer, InstructionStepSerializer
from django.utils import timezone
import json
import os

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().order_by('-created_at')
    serializer_class = DocumentSerializer

    @action(detail=False, methods=['post'])
    def create_from_template(self, request):
        doc_type = request.data.get('doc_type')
        if not doc_type:
            return Response({'error': 'doc_type required'}, status=status.HTTP_400_BAD_REQUEST)

        # Load from template
        template_path = os.path.join('templates', f'{doc_type}_template.json')
        if not os.path.exists(template_path):
            name = f"New {doc_type.capitalize()}"
        else:
            with open(template_path, 'r') as f:
                template = json.load(f)
                name = template.get('name', f"New {doc_type.capitalize()}")

        doc = Document.objects.create(doc_type=doc_type, name=name)

        if doc_type == Document.TRAVELER:
            traveler = Traveler.objects.create(document=doc)
            if os.path.exists(template_path):
                with open(template_path, 'r') as f:
                    template = json.load(f)
                    for step in template.get('steps', []):
                        TravelerStep.objects.create(
                            traveler=traveler,
                            step_number=step['step_number'],
                            label=step['label']
                        )
            else:
                # Fallback
                for i, label in enumerate(['step 1', 'step 2', 'step 3', 'step 4', 'step 5']):
                    step_num = (i + 1) * 10
                    TravelerStep.objects.create(traveler=traveler, step_number=step_num, label=label)

        elif doc_type == Document.INSTRUCTIONS:
            instruction = Instruction.objects.create(document=doc)
            if os.path.exists(template_path):
                with open(template_path, 'r') as f:
                    template = json.load(f)
                    for step in template.get('steps', []):
                        InstructionStep.objects.create(
                            instruction=instruction,
                            step_number=step['step_number'],
                            instruction_text=step['instruction_text'],
                            entry_values=['' for _ in range(step['instruction_text'].count('{{entry}}'))]
                        )

        return Response(DocumentSerializer(doc).data, status=status.HTTP_201_CREATED)

class TravelerStepViewSet(viewsets.ModelViewSet):
    queryset = TravelerStep.objects.all()
    serializer_class = TravelerStepSerializer

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

class InstructionStepViewSet(viewsets.ModelViewSet):
    queryset = InstructionStep.objects.all()
    serializer_class = InstructionStepSerializer
