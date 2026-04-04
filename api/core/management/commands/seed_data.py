import json
from django.core.management.base import BaseCommand
from core.models import Template, DocumentInstance

class Command(BaseCommand):
    help = 'Seed the database with initial JSON Forms templates and documents'

    def handle(self, *args, **kwargs):
        # Clear existing
        DocumentInstance.objects.all().delete()
        Template.objects.all().delete()

        # 1. Create a Simple Template
        schema = {
          "type": "object",
          "properties": {
            "name": { "type": "string" },
            "description": { "type": "string" },
            "done": { "type": "boolean" }
          }
        }
        uischema = {
          "type": "VerticalLayout",
          "elements": [
            { "type": "Control", "scope": "#/properties/name" },
            { "type": "Control", "scope": "#/properties/description" },
            { "type": "Control", "scope": "#/properties/done" }
          ]
        }

        template = Template.objects.create(
            name="Simple Task",
            description="A simple task template using JSON Forms",
            schema=schema,
            uischema=uischema,
            status="Active"
        )

        # Create an instance
        DocumentInstance.objects.create(
            template=template,
            title="First Task",
            data={
                "name": "Implement JSON Forms",
                "description": "Switch from form-create to jsonforms",
                "done": True
            },
            status="Active"
        )

        # 2. Mixture Record Template
        mr_schema = {
            "type": "object",
            "properties": {
                "doc_type": { "type": "string" },
                "mrn": { "type": "string" },
                "notes": { "type": "string" }
            }
        }
        mr_uischema = {
            "type": "VerticalLayout",
            "elements": [
                {
                    "type": "Control",
                    "scope": "#/properties/doc_type",
                    "label": "MR",
                    "options": { "type": "DocumentType" }
                },
                {
                    "type": "Control",
                    "scope": "#/properties/mrn",
                    "label": "Mixture Record Number",
                    "options": { "type": "MixtureRecordNumber" }
                },
                { "type": "Control", "scope": "#/properties/notes" }
            ]
        }

        Template.objects.create(
            name="Mixture Record Template",
            description="Template with MRN",
            schema=mr_schema,
            uischema=mr_uischema,
            status="Active"
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded JSON Forms templates and documents'))
