from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from guests.models import Reservation
from syncer.sync import AirbnbAPI


class Command(BaseCommand):
    help = "A tick o' the worker"

    def add_arguments(self, parser):
        parser.add_argument('--sync-airbnb',
            action='store_true',
            dest='sync_airbnb',
            default=False,
            help='Fetch reservations from airbnb and save them')

        parser.add_argument('--send-daily-email',
            action='store_true',
            dest='send_daily_email',
            default=False,
            help='Shoot out the daily summary email to owners')

    def handle(self, *args, **options):
        if options['sync_airbnb']:
            self.sync_airbnb()
        if options['send_daily_email']:
            self.send_daily_email()
        self.stdout.write(self.style.SUCCESS("Tock."))

    def sync_airbnb(self):
        airbnb = AirbnbAPI(settings.AIRBNB_USERNAME, settings.AIRBNB_PASSWORD)
        resos = airbnb.get_all_reservations()

        Reservation.objects.all().delete()  # lol

        for confirmation_code, reso in resos.items():
            Reservation.objects.create(
                confirmation_code=confirmation_code,
                dates=(reso["start_date"], reso["end_date"]),
                guest=reso['guest'],
                thread_id=reso.get('thread_id', ''))
            self.stdout.write("Saved new reservation: %s" % reso['guest'].get('full_name', '<no name>'))

        self.stdout.write(
            self.style.SUCCESS("Now have %s reservations in the database!" % Reservation.objects.count()))

    def send_daily_email(self):
        self.stdout.write("<<<TODO: send daily email>>>")
