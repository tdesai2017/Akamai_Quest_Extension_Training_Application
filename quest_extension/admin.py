from django.contrib import admin
from quest_extension.models import *

# Register your models here.
admin.site.register(User)
admin.site.register(CompletedQuest)
admin.site.register(CorrectAnswer)
admin.site.register(Quest)
admin.site.register(Question)
admin.site.register(IncorrectAnswer)

