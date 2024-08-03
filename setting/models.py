from django.db import models
from mdeditor.fields import MDTextField


class Rule(models.Model):
    title = models.CharField(max_length=100)
    short_desc = models.CharField(max_length=100)
    content = MDTextField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        rules = Rule.objects.filter(is_active=True).first()
        if rules and self.id != rules.id:
            self.is_active = False
        super(Rule, self).save(*args, **kwargs)
