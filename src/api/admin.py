from django.contrib import admin
from .models import CustomUser, ChatSession, ChatMessage
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(ChatSession)
admin.site.register(ChatMessage)
