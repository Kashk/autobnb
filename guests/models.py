from django.contrib.postgres.fields import DateRangeField, JSONField
from django.db import models


class Reservation(models.Model):
    confirmation_code = models.CharField(max_length=10, unique=True)
    thread_id = models.CharField(max_length=10, blank=True, null=True)
    dates = DateRangeField()
    guest = JSONField()
