from django.contrib import admin
from chat.models import Message

class MessageAdmin(admin.ModelAdmin):
    search_fields = ['posted_by', 'text']

admin.site.register(Message, MessageAdmin)
