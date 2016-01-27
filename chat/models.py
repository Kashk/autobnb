from django.db import models


class Message(models.Model):
    reso = models.ForeignKey('guests.Reservation')
    text = models.TextField()
    posted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

    @property
    def posted_by(self):
        return "%s from %s" (self.reso.name, self.reso.location)

    @property
    def thumbnail(self):
        return self.reso.picture
