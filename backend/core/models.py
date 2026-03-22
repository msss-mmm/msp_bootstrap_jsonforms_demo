from django.db import models
import json
import os
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Sync to directory
        templates_dir = os.path.join(settings.BASE_DIR, 'templates')
        os.makedirs(templates_dir, exist_ok=True)
        filename = f"{self.name.lower().replace(' ', '_')}_template.json"
        filepath = os.path.join(templates_dir, filename)
        data = {
            "name": self.name,
            "description": self.description,
            "rule": self.rule,
            "options": self.options,
            "status": self.status
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
