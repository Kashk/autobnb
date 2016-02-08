import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.template.loader import render_to_string

from guests.models import Reservation, ReservationLog
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

        parser.add_argument('--send-checkin-msg',
            action='store_true',
            dest='send_checkin_msg',
            default=False,
            help='Send Airbnb checkin msg to people checking in within 3 days')

        parser.add_argument('--send-guest2guest-link',
            action='store_true',
            dest='send_guest2guest_link',
            default=False,
            help='Send guest2guest link to people checking in today')

    def handle(self, *args, **options):
        self.airbnb = AirbnbAPI(settings.AIRBNB_USERNAME, settings.AIRBNB_PASSWORD)

        if options['sync_airbnb']:
            self.sync_airbnb()
        if options['send_daily_email']:
            self.send_daily_email()
        if options['send_checkin_msg']:
            self.send_checkin_msg()
        if options['send_guest2guest_link']:
            self.send_guest2guest_link()
        self.stdout.write(self.style.SUCCESS("Tock."))

    def sync_airbnb(self):
        resos = self.airbnb.get_all_reservations()

        Reservation.objects.all().delete()  # lol

        for confirmation_code, reso in resos.items():
            Reservation.objects.create(
                confirmation_code=confirmation_code,
                dates=(reso["start_date"], reso["end_date"]),
                guest=reso['guest'],
                thread_id=reso.get('thread_id', ''))
            self.stdout.write("Saved new reservation: %s" % confirmation_code)

        self.stdout.write(
            self.style.SUCCESS("Now have %s reservations in the database!" % Reservation.objects.count()))

    def send_daily_email(self):
        self.stdout.write("<<<TODO: send daily email>>>")

    def send_checkin_msg(self):
        already_sent_resos = ReservationLog.objects.filter(action='send_checkin_msg')
        codes = [r.confirmation_code for r in already_sent_resos]
        resos = Reservation.objects.exclude(
            confirmation_code__in=codes).exclude(
            thread_id=None).exclude(
            thread_id='').filter(
                Q(dates__startswith=datetime.date.today()) |
                Q(dates__startswith=datetime.date.today() + datetime.timedelta(days=1)) |
                Q(dates__startswith=datetime.date.today() + datetime.timedelta(days=2)) |
                Q(dates__startswith=datetime.date.today() + datetime.timedelta(days=3)))
        
        msg = render_to_string('checkin_msg.txt', {})

        for reso in resos:
            print("Sending check-in msg to: %s" % reso.name)
            self.airbnb.send_message(reso.thread_id, msg)
            ReservationLog.objects.create(confirmation_code=reso.confirmation_code, action='send_checkin_msg')

    def send_guest2guest_link(self):
        already_sent_resos = ReservationLog.objects.filter(action='send_guest2guest_link')
        codes = [r.confirmation_code for r in already_sent_resos]
        resos = Reservation.objects.exclude(
            confirmation_code__in=codes).exclude(
            thread_id=None).exclude(
            thread_id='').filter(dates__startswith=datetime.date.today())

        for reso in resos:
            print("Sending guest2guest link to: %s" % reso.name)
            msg = render_to_string('guest2guest_link_msg.txt', {'reso': reso, 'DOMAIN': settings.DOMAIN})
            self.airbnb.send_message(reso.thread_id, msg)
            ReservationLog.objects.create(confirmation_code=reso.confirmation_code, action='send_guest2guest_link')
