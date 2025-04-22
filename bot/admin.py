from django.contrib import admin

# Register your models here.

from .models import Grade, Language, Question, Sphere, User

admin.site.register(Grade)
admin.site.register(Language)
admin.site.register(Question)
admin.site.register(Sphere)
admin.site.register(User)

