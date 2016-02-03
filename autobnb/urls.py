from django.conf.urls import patterns, include, url
from django.contrib import admin
import chat.views

urlpatterns = [
    url(r'^$', chat.views.root),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^reso/(?P<confirmation_code>\w+)$', chat.views.reso, name='reso-home'),
    url(r'^resident/(?P<slug>\w+)$', chat.views.resident, name='resident-home'),
]
