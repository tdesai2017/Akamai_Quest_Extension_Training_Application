from django.urls import path
from . import views
from django.conf.urls import url


urlpatterns = [
    path('', views.home, name='quest-home'),
    path('quest-create-form', views.quest_create, name='quest_form'),
    #path('choose-mc-or-fr/<name>', views.choose_question_type),
    path('mc-create-form/<quest_id>', views.create_mc_question),
    path('fr-create-form/<quest_id>', views.create_fr_question),
    #path('more_questions/<name>', views.more_questions),
    #path('home', views.quest_home, name='home'),
    path('admin_home/<project_id>', views.admin_home),
    path('admin_quest_page/<quest_id>', views.admin_quest_page),
    path('user_home/<ldap>/<project_id>', views.user_home),
    path('user_quest_page/<ldap>/<quest_id>', views.user_quest_page),
    path('admin_edit_question/<question_id>', views.admin_edit_question),
    path('admin_project_page', views.admin_project_page)

]
