import datetime

from django.http import HttpResponseNotFound, HttpResponseGone
from django.shortcuts import render

from guests.models import Reservation


def reso(request, confirmation_code):
    try:
        reso = Reservation.objects.get(confirmation_code=confirmation_code)
    except Reservation.DoesNotExist:
        return HttpResponseNotFound("Your reservation confirmation code wasn't found.")

    if reso.dates.upper < datetime.date.today() - datetime.timedelta(days=2):
        return HttpResponseGone("Sorry! Your reservation ended already, so you can't see this anymore.")

    if 'msg' in request.POST:
        pass

    return render(request, 'reso.html', {})
