import datetime

from django.http import HttpResponseNotFound, HttpResponseGone, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from chat.models import Message
from guests.models import Reservation, Resident


def render_chat_page(request):
    start_date = timezone.now() - datetime.timedelta(days=7)
    end_date = timezone.now()
    messages = Message.objects.filter(posted_on__range=(start_date, end_date))
    all_resos = Reservation.objects.filter(dates__contains=datetime.date.today())

    return render(request, 'reso.html', {'reso': reso, 'messages': messages, 'all_resos': all_resos})


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

    return render_chat_page(request)
