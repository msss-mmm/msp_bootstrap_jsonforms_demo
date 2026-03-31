import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Template

class Command(BaseCommand):
    help = 'Prime the database from the templates directory'

    def handle(self, *args, **options):
        templates_dir = os.path.join(settings.BASE_DIR, 'templates')
        if not os.path.exists(templates_dir):
            self.stdout.write(self.style.WARNING(f'Templates directory {templates_dir} does not exist.'))
            return

        for filename in os.listdir(templates_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(templates_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)

                    name = data.get('name')
                    if not name:
                        continue

                    schema = data.get('schema', {})
                    uischema = data.get('uischema', {})
                    status = data.get('status')
                    if not status:
                        is_active = data.get('is_active', True)
                        status = 'Active' if is_active else 'Inactive'
                    description = data.get('description', '')

                    template, created = Template.objects.update_or_create(
                        name=name,
                        defaults={
                            'schema': schema,
                            'uischema': uischema,
                            'status': status,
                            'description': description
                        }
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created template: {name}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Updated template: {name}'))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing {filename}: {str(e)}'))
