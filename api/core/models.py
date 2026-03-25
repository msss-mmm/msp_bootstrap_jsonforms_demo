from django.db import models
import json
import os
import urllib.parse
from django.conf import settings

class Template(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Archived', 'Archived'),
    ]
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    rule = models.JSONField(help_text="FormCreate rules (JSON)")
    options = models.JSONField(default=dict, blank=True, help_text="FormCreate options (JSON)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_template_filename(self):
        """Returns the filename for this template."""
        safe_name = urllib.parse.quote(self.name, safe='')
        return f"{self.id}_{safe_name}_template.json"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Sync to directory
        templates_dir = os.path.join(settings.BASE_DIR, 'templates')
        os.makedirs(templates_dir, exist_ok=True)

        filename = self.get_template_filename()
        filepath = os.path.join(templates_dir, filename)
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "rule": self.rule,
            "options": self.options,
            "status": self.status,
            "CreatedAt": self.created_at.isoformat() if self.created_at else None,
            "UpdatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

class DocumentInstance(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Locked', 'Locked'),
        ('Archived', 'Archived'),
    ]
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='instances')
    title = models.CharField(max_length=255)
    data = models.JSONField(default=dict, blank=True, help_text="Form data (JSON)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.template.name})"

    def get_document_filename(self):
        """Returns the filename for this document."""
        safe_title = urllib.parse.quote(self.title, safe='')
        return f"{self.id}_{safe_title}.json"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Sync to directory
        documents_dir = os.path.join(settings.BASE_DIR, 'documents')
        os.makedirs(documents_dir, exist_ok=True)

        filename = self.get_document_filename()
        filepath = os.path.join(documents_dir, filename)
        data = {
            "id": self.id,
            "template_name": self.template.name,
            "title": self.title,
            "data": self.data,
            "status": self.status,
            "CreatedAt": self.created_at.isoformat() if self.created_at else None,
            "UpdatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
