import datetime

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseGone, HttpResponseRedirect
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


message_template = """"A guest at the hostel posted this message for everyone:

%s
-- %s

You can respond here:
%s%s

PS: This is an automated message we're testing out. If this is fun or annoying, give us some feedback!"""

def new_message_notification(posted_by, text):
    airbnb = AirbnbAPI(settings.AIRBNB_USERNAME, settings.AIRBNB_PASSWORD)

    resos = Reservation.objects.filter(dates__contains=datetime.date.today()
        ).exclude(thread_id=None).exclude(thread_id="")
    
    for reso in resos:
        message = message_template % (text, posted_by, settings.DOMAIN, reso.get_absolute_url())
        airbnb.send_message(reso.thread_id, message)

    residents = Resident.objects.filter(is_active=True
        ).exclude(thread_id=None).exclude(thread_id="")

    for resident in residents:
        message = message_template % (text, posted_by, settings.DOMAIN, resident.get_absolute_url())
        airbnb.send_message(resident.thread_id, message)

    # thread_ids = [152531217]  # hardcoded to Duncan
    # resos = Reservation.objects.filter(dates__contains=datetime.date.today()
    #     ).exclude(thread_id=None).exclude(thread_id="")
    # residents = Resident.objects.filter(is_active=True
    #     ).exclude(thread_id=None).exclude(thread_id="")
    # names = [reso.name for reso in resos] + [resident.label for resident in residents]


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


def root(request):
    return HttpResponse("Hello there! Go check your Airbnb messages for a link to access this thing.")
