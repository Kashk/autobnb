import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from guests.models import Reservation


class Command(BaseCommand):
    help = "show who's staying tonight!"

    def handle(self, *args, **options):
        resos = Reservation.objects.filter(dates__contains=datetime.date.today())
        for reso in resos:
            self.stdout.write("%s: %s" % (reso.confirmation_code, reso.name))
