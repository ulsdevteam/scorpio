from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class IndexRun(models.Model):
    STARTED = 0
    FINISHED = 1
    ERRORED = 2
    STATUS_CHOICES = (
        (STARTED, 'Started'),
        (FINISHED, 'Finished'),
        (ERRORED, 'Errored'),
    )
    OBJECT_TYPE_CHOICES = (
        ("agent", "Agent"),
        ("collection", "Collection"),
        ("object", "Object"),
        ("term", "Term")
    )
    OBJECT_STATUS_CHOICES = (("indexed", "Indexed"), ("deleted", "Deleted"))
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    object_type = models.CharField(max_length=100, choices=OBJECT_TYPE_CHOICES, blank=True, null=True)
    object_status = models.CharField(max_length=100, choices=OBJECT_STATUS_CHOICES)

    @property
    def errors(self):
        return IndexRunError.objects.filter(run=self)

    @property
    def error_count(self):
        return len(IndexRunError.objects.filter(run=self))

    @property
    def elapsed(self):
        if (self.end_time and self.end_time):
            return self.end_time - self.start_time
        return 0


class IndexRunError(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    message = models.TextField(max_length=255)
    run = models.ForeignKey(IndexRun, on_delete=models.CASCADE)

    class Meta:
        ordering = ('datetime', )
