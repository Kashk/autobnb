from django.db import models


class Message(models.Model):
    posted_by = models.CharField(max_length=100)
    picture = models.URLField(default="https://i.imgur.com/WBdUBl0.jpg")
    text = models.TextField()
    posted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s: %s" % (self.posted_by, self.text)
