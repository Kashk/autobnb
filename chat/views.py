import datetime

from django.http import HttpResponseNotFound, HttpResponseGone
from django.shortcuts import render
from django.utils import timezone

from chat.models import Message
from guests.models import Reservation


def reso(request, confirmation_code):
    try:
        reso = Reservation.objects.get(confirmation_code=confirmation_code)
    except Reservation.DoesNotExist:
        return HttpResponseNotFound("Your reservation confirmation code wasn't found.")

    if reso.dates.upper < datetime.date.today() - datetime.timedelta(days=2):
        return HttpResponseGone("Sorry! Your reservation ended already, so you can't see this anymore.")

    if 'msg' in request.POST:
        Message.objects.create(text=request.POST['msg'], reso=reso)

    start_date = timezone.now() - datetime.timedelta(days=7)
    end_date = timezone.now()
    messages = Message.objects.filter(posted_on__range=(start_date, end_date))

    return render(request, 'reso.html', {'reso': reso, 'messages': messages})
