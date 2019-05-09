from django.contrib import admin
from quest_extension.models import *

from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

# Register your models here.
admin.site.register(User)
admin.site.register(CompletedQuest)
admin.site.register(CorrectAnswer)
admin.site.register(Quest)
admin.site.register(Question)
admin.site.register(IncorrectAnswer)
admin.site.register(Project)
admin.site.register(CorrectlyAnsweredQuestion)
admin.site.register(UserProject)

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username',]

admin.site.register(CustomUser, CustomUserAdmin)

