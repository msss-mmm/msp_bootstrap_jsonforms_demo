from rest_framework import serializers
from .models import Template, DocumentInstance

class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = '__all__'

class DocumentInstanceSerializer(serializers.ModelSerializer):
    template_name = serializers.ReadOnlyField(source='template.name')
    operator_status = serializers.SerializerMethodField()
    qa_status = serializers.SerializerMethodField()

    class Meta:
        model = DocumentInstance
        fields = '__all__'

    def get_approval_status(self, obj, component_type):
        """
        Helper to determine the approval status for a given component type.
        Returns: 'none', 'partial', or 'full'.
        """
        template_rule = obj.template.rule
        if not isinstance(template_rule, list):
            return 'none'

        field_names = []

        def find_fields(rules):
            for r in rules:
                if r.get('type') == component_type:
                    field_names.append(r.get('field'))
                if 'children' in r:
                    find_fields(r['children'])
                if 'control' in r:
                    for c in r['control']:
                        if 'rule' in c:
                            find_fields(c['rule'])

        find_fields(template_rule)

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
