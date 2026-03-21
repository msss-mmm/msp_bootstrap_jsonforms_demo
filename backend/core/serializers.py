from rest_framework import serializers
from .models import Template, DocumentInstance

class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = '__all__'

class DocumentInstanceSerializer(serializers.ModelSerializer):
    template_name = serializers.ReadOnlyField(source='template.name')

    class Meta:
        model = DocumentInstance
        fields = '__all__'
