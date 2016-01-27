from django.core.management.base import BaseCommand, CommandError


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
        self.stdout.write("sync-airbnb: %s" % options['sync_airbnb'])
        self.stdout.write("send-daily-email: %s" % options['send_daily_email'])
        self.stdout.write(self.style.SUCCESS("You are worth something!"))
