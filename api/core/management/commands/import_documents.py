import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Template, DocumentInstance

class Command(BaseCommand):
    help = 'Import documents from the documents directory'

    def handle(self, *args, **options):
        documents_dir = os.path.join(settings.BASE_DIR, 'documents')
        if not os.path.exists(documents_dir):
            self.stdout.write(self.style.WARNING(f'Documents directory {documents_dir} does not exist.'))
            return

        for filename in os.listdir(documents_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(documents_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)

                    title = data.get('title')
                    template_name = data.get('template_name')

                    if not title or not template_name:
                        self.stdout.write(self.style.ERROR(f'Missing title or template_name in {filename}'))
                        continue

                    try:
                        template = Template.objects.get(name=template_name)
                    except Template.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f'Template "{template_name}" not found for document "{title}" in {filename}. Skipping.'))
                        continue

                    doc_id = data.get('id')
                    doc_data = data.get('data', {})
                    status = data.get('status', 'Active')

                    if doc_id:
                        doc, created = DocumentInstance.objects.update_or_create(
                            id=doc_id,
                            defaults={
                                'template': template,
                                'title': title,
                                'data': doc_data,
                                'status': status
                            }
                        )
                    else:
                        doc = DocumentInstance.objects.create(
                            template=template,
                            title=title,
                            data=doc_data,
                            status=status
                        )
                        created = True

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created document: {title} (ID: {doc.id})'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Updated document: {title} (ID: {doc.id})'))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing {filename}: {str(e)}'))
