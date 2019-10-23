from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField


class User(AbstractUser):
    pass


class DataObject(models.Model):
    TYPE_CHOICES = (
        ('agent', 'Agent'),
        ('collection', 'Collection'),
        ('object', 'Object'),
        ('term', 'Term'),
    )
    es_id = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES)
    data = JSONField()
    indexed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
