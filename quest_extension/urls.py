from django.urls import path
from . import views
from django.conf.urls import url


urlpatterns = [
    path('', views.home, name='quest-home'),
    path('quest-create-form', views.quest_create, name='quest_form'),
    #path('choose-mc-or-fr/<name>', views.choose_question_type),
    path('mc-create-form/<name>', views.create_mc_question),
    path('fr-create-form/<name>', views.create_fr_question),
    #path('more_questions/<name>', views.more_questions),
    #path('home', views.quest_home, name='home'),
    path('admin_home', views.admin_home),
    path('admin_quest_page/<name>', views.admin_quest_page),
    path('user_home/<ldap>', views.user_home),
    path('user_quest_page/<ldap>/<name>', views.user_quest_page),
]
