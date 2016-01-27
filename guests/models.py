from django.contrib.postgres.fields import DateRangeField, JSONField
from django.db import models


class Reservation(models.Model):
    confirmation_code = models.CharField(max_length=10, unique=True)
    dates = DateRangeField()
    guest = JSONField()
