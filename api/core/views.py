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
