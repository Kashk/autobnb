from django.conf.urls import patterns, include, url
from django.contrib import admin
import chat.views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^reso/(?P<confirmation_code>\w+)$', chat.views.reso),
]
