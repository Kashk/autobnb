import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from guests.models import Reservation, Resident


class Command(BaseCommand):
    help = "show who's staying tonight!"

    def handle(self, *args, **options):
        resos = Reservation.objects.filter(dates__contains=datetime.date.today())
        for reso in resos:
            if reso.thread_id:
                self.stdout.write("%s: %s" % (reso.confirmation_code, reso.name))
            else:
                self.stdout.write("%s: %s (no thread_id!!!)" % (reso.confirmation_code, reso.name))

        self.stdout.write("----- now residents! ------")

        residents = Resident.objects.filter(is_active=True)
        for resident in residents:
            if resident.thread_id:
                self.stdout.write("%s: %s" % (resident.slug, resident.label))
            else:
                self.stdout.write("%s: %s (no thread_id!!!)" % (resident.slug, resident.label))
