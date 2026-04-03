import json
from django.core.management.base import BaseCommand
from core.models import Template, DocumentInstance

class Command(BaseCommand):
    help = 'Seed the database with a regression template for alignment testing'

    def handle(self, *args, **kwargs):
        # Clear existing
        DocumentInstance.objects.all().delete()
        Template.objects.all().delete()

        schema = {
          "type": "object",
          "properties": {
            "text1": { "type": "string" },
            "text2": { "type": "string", "readOnly": True },
            "date1": { "type": "string", "format": "date" },
            "date2": { "type": "string", "format": "date", "readOnly": True },
            "bool1": { "type": "boolean" },
            "bool2": { "type": "boolean", "readOnly": True },
            "num1": { "type": "number" },
            "num2": { "type": "number", "readOnly": True },
            "mrn": { "type": "string" }
          }
        }

        uischema = {
          "type": "VerticalLayout",
          "elements": [
            {
              "type": "HorizontalLayout",
              "elements": [
                { "type": "Control", "scope": "#/properties/text1", "label": "Text Input" },
                { "type": "Control", "scope": "#/properties/text2", "label": "Read-only Text" }
              ]
            },
            {
              "type": "HorizontalLayout",
              "elements": [
                { "type": "Control", "scope": "#/properties/date1", "label": "Date Picker" },
                { "type": "Control", "scope": "#/properties/date2", "label": "Read-only Date" }
              ]
            },
            {
              "type": "HorizontalLayout",
              "elements": [
                { "type": "Control", "scope": "#/properties/bool1", "label": "Boolean/Check" },
                { "type": "Control", "scope": "#/properties/bool2", "label": "Read-only Boolean" }
              ]
            },
            {
              "type": "HorizontalLayout",
              "elements": [
                { "type": "Control", "scope": "#/properties/num1", "label": "Number Input" },
                { "type": "Control", "scope": "#/properties/num2", "label": "Read-only Number" }
              ]
            },
            {
              "type": "Control",
              "scope": "#/properties/mrn",
              "options": { "type": "MixtureRecordNumber" }
            }
          ]
        }

        template = Template.objects.create(
            name="Alignment Test",
            description="Testing vertical and horizontal alignment",
            schema=schema,
            uischema=uischema,
            status="Active"
        )

        DocumentInstance.objects.create(
            template=template,
            title="Alignment Regression Document",
            data={
                "text1": "Editable Text",
                "text2": "Read-only Text Value",
                "date1": "2023-10-27",
                "date2": "2023-10-27",
                "bool1": True,
                "bool2": False,
                "num1": 123.45,
                "num2": 678.90,
                "mrn": "231027A_mr"
            },
            status="Active"
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded alignment test data'))
