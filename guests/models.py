from django.contrib.postgres.fields import DateRangeField, JSONField
from django.db import models


class Reservation(models.Model):
    confirmation_code = models.CharField(max_length=10, unique=True)
    thread_id = models.CharField(max_length=10, blank=True, null=True)
    dates = DateRangeField()
    guest = JSONField()

    @property
    def name(self):
        if 'full_name' in self.guest:
            return self.guest['full_name']
        elif 'first_name' in self.guest:
            return self.guest['first_name']
        else:
            return "[unknown name]"

    @property
    def location(self):
        if 'location' in self.guest:
            return self.guest['location']
        else:
            return "[unknown location]"

    @property
    def picture(self):
        if 'picture_url' in self.guest:
            return self.guest['picture_url']
        else:
            return "https://i.imgur.com/WBdUBl0.jpg"

    def __str__(self):
        return "%s - %s" % (self.confirmation_code, self.name)


class Resident(models.Model):
    was_reso = models.CharField(max_length=10, unique=True, blank=True)
    thread_id = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    slug = models.SlugField()

    label = models.CharField(max_length=75, unique=True)
    picture = models.URLField(default="https://i.imgur.com/WBdUBl0.jpg")

    guest = JSONField(null=True, blank=True)

    def __str__(self):
        return self.label
