from django.conf.urls import patterns, include, url
from django.contrib import admin
import guests.views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^reso/$', guests.views.reso),
]
