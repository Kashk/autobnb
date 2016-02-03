import datetime

from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponseGone, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from chat.models import Message
from guests.models import Reservation, Resident
from syncer.sync import AirbnbAPI


def render_chat_page(request):
    start_date = timezone.now() - datetime.timedelta(days=7)
    end_date = timezone.now()
    messages = Message.objects.filter(posted_on__range=(start_date, end_date))
    all_resos = Reservation.objects.filter(dates__contains=datetime.date.today())
    all_residents = Resident.objects.filter(is_active=True).order_by('id')

    return render(request, 'reso.html', {
        'messages': messages,
        'all_resos': all_resos,
        'all_residents': all_residents,
    })


def new_message_notification(posted_by, text):
    resos = Reservation.objects.filter(dates__contains=datetime.date.today()
        ).exclude(thread_id=None).exclude(thread_id="").values_list('thread_id', flat=True)
    residents = Resident.objects.filter(is_active=True
        ).exclude(thread_id=None).exclude(thread_id="").values_list('thread_id', flat=True)

    thread_ids = list(resos) + list(residents)

    thread_ids = [152531217]  # hardcoded to Duncan
    resos = Reservation.objects.filter(dates__contains=datetime.date.today()
        ).exclude(thread_id=None).exclude(thread_id="")
    residents = Resident.objects.filter(is_active=True
        ).exclude(thread_id=None).exclude(thread_id="")
    names = [reso.name for reso in resos] + [resident.label for resident in residents]

    message = """
Hi! This message was sent to the whole house.
%s says: %s
DEBUG INFO: This notification would've been sent to: %s
""" % (posted_by, text, names)

    airbnb = AirbnbAPI(settings.AIRBNB_USERNAME, settings.AIRBNB_PASSWORD)
    for thread_id in thread_ids:
        airbnb.send_message(thread_id, message)


def reso(request, confirmation_code):
    resident = Resident.objects.filter(was_reso=confirmation_code)
    if resident.exists():
        return HttpResponseRedirect("/resident/%s" % resident.get().slug)

    try:
        reso = Reservation.objects.get(confirmation_code=confirmation_code)
    except Reservation.DoesNotExist:
        return HttpResponseNotFound("Your reservation confirmation code wasn't found.")

    if reso.dates.upper < datetime.date.today() - datetime.timedelta(days=2):
        return HttpResponseGone("Sorry! Your reservation ended already so you can't see this anymore.")

    if 'msg' in request.POST:
        posted_by = "%s from %s" % (reso.name, reso.location)
        picture = reso.picture
        Message.objects.create(text=request.POST['msg'], posted_by=posted_by, picture=picture)
        new_message_notification(posted_by, request.POST['msg'])

    return render_chat_page(request)


def resident(request, slug):
    try:
        resident = Resident.objects.get(slug=slug)
    except Resident.DoesNotExist:
        return HttpResponseNotFound("Your resident code wasn't found.")

    if not resident.is_active:
        return HttpResponseGone("Sorry! This resident code doesn't work anymore.")

    if 'msg' in request.POST:
        posted_by = resident.label
        picture = resident.picture
        Message.objects.create(text=request.POST['msg'], posted_by=posted_by, picture=picture)
        new_message_notification(posted_by, request.POST['msg'])

    return render_chat_page(request)
