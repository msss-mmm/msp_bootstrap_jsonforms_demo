from rest_framework import serializers
from .models import Template, DocumentInstance

class TemplateSerializer(serializers.ModelSerializer):
    document_count = serializers.SerializerMethodField()

    class Meta:
        model = Template
        fields = '__all__'

    def get_document_count(self, obj):
        return obj.instances.count()

class DocumentInstanceSerializer(serializers.ModelSerializer):
    template_name = serializers.ReadOnlyField(source='template.name')
    operator_status = serializers.SerializerMethodField()
    qa_status = serializers.SerializerMethodField()
    mixture_record_number = serializers.SerializerMethodField()

    class Meta:
        model = DocumentInstance
        fields = '__all__'

    def get_approval_status(self, obj, component_type):
        """
        Helper to determine the approval status for a given component type.
        Returns: 'none', 'partial', or 'full'.
        """
        # For JSON Forms, we'll look into the uischema for custom elements
        uischema = obj.template.uischema
        if not isinstance(uischema, dict):
            return 'none'

        field_names = []

        def find_fields(element):
            if not isinstance(element, dict):
                return

            # JSON Forms uischema elements usually have a 'type' and sometimes a 'scope'
            # Custom renderers might be identified by 'options.type' or similar
            if element.get('options', {}).get('type') == component_type:
                scope = element.get('scope')
                if scope and scope.startswith('#/properties/'):
                    field_names.append(scope.split('/')[-1])

            # Recurse into layouts
            if 'elements' in element and isinstance(element['elements'], list):
                for child in element['elements']:
                    find_fields(child)

            if 'options' in element and isinstance(element['options'], dict):
                # Some options might contain elements
                if 'elements' in element['options'] and isinstance(element['options']['elements'], list):
                    for child in element['options']['elements']:
                        find_fields(child)

        find_fields(uischema)

        if not field_names:
            return 'none'

        signed_count = 0
        for field in field_names:
            val = obj.data.get(field)
            if val and isinstance(val, dict) and val.get('name'):
                signed_count += 1

        if signed_count == 0:
            return 'none'
        elif signed_count < len(field_names):
            return 'partial'
        else:
            return 'full'

    def get_operator_status(self, obj):
        return self.get_approval_status(obj, 'OperatorApprove')

    def get_qa_status(self, obj):
        return self.get_approval_status(obj, 'QAApprove')

    def get_mixture_record_number(self, obj):
        """
        Helper to find the mixture record number in the document data.
        """
        uischema = obj.template.uischema
        if not isinstance(uischema, dict):
            return None

        field_name = None

        def find_mrn_field(element):
            nonlocal field_name
            if field_name or not isinstance(element, dict):
                return

            if element.get('options', {}).get('type') == 'MixtureRecordNumber':
                scope = element.get('scope')
                if scope and scope.startswith('#/properties/'):
                    field_name = scope.split('/')[-1]

            if 'elements' in element and isinstance(element['elements'], list):
                for child in element['elements']:
                    find_mrn_field(child)

        find_mrn_field(uischema)

        if field_name:
            return obj.data.get(field_name)

        return None
