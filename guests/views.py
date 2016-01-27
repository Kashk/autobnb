from django.shortcuts import render


def reso(request):
    return render(request, 'reso.html', {})
