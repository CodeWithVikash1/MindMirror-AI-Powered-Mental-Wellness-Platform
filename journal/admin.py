from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(EmailOTP)
admin.site.register(MoodEntry)
admin.site.register(Reflection)