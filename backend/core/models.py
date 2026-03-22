from django.db import models
import json
import os
import urllib.parse
from django.conf import settings

class Template(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    rule = models.JSONField(help_text="FormCreate rules (JSON)")
    options = models.JSONField(default=dict, blank=True, help_text="FormCreate options (JSON)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_template_filename(self):
        """Returns the filename for this template, maintaining backward compatibility."""
        # Old format: name.lower().replace(' ', '_') + '_template.json'
        old_filename = f"{self.name.lower().replace(' ', '_')}_template.json"
        templates_dir = os.path.join(settings.BASE_DIR, 'templates')
        old_filepath = os.path.join(templates_dir, old_filename)

        if os.path.exists(old_filepath):
            return old_filename

        # New format (safe): URL-encoded name
        safe_name = urllib.parse.quote(self.name, safe='')
        return f"{safe_name}_template.json"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Sync to directory
        templates_dir = os.path.join(settings.BASE_DIR, 'templates')
        os.makedirs(templates_dir, exist_ok=True)

        filename = self.get_template_filename()
        filepath = os.path.join(templates_dir, filename)
        data = {
            "name": self.name,
            "description": self.description,
            "rule": self.rule,
            "options": self.options,
            "is_active": self.is_active
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

class DocumentInstance(models.Model):
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='instances')
    title = models.CharField(max_length=255)
    data = models.JSONField(default=dict, blank=True, help_text="Form data (JSON)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.template.name})"
