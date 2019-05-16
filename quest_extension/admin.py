from django.contrib import admin
from quest_extension.models import *

from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

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
admin.site.register(Video)
admin.site.register(Admin)
admin.site.register(AdminProject)


