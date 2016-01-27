from django.contrib.postgres.fields import DateRangeField, JSONField
from django.db import models


class Reservation(models.Model):
    confirmation_code = models.CharField(max_length=10, unique=True)
    thread_id = models.CharField(max_length=10, blank=True, null=True)
    dates = DateRangeField()
    guest = JSONField()

    def name(self):
        if 'full_name' in self.guest:
            return self.guest['full_name']
        elif 'name' in self.guest:
            return self.guest['name']
        else:
            return "[unknown name]"

    def __str__(self):
        return "%s - %s" % (self.confirmation_code, self.name)
