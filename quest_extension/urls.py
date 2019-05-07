from django.urls import path
from . import views
from django.conf.urls import url


urlpatterns = [
    #Decides what Question Admin wants to create
    path('mc-create-form/<quest_id>', views.create_mc_question),
    path('fr-create-form/<quest_id>', views.create_fr_question),

    #Admin Pages
    path('admin_home_editable/<project_id>', views.admin_home_editable),
    path('admin_quest_page_editable/<quest_id>', views.admin_quest_page_editable),
    path('admin_project_page', views.admin_project_page),
    path('admin_home_view_only/<project_id>', views.admin_home_view_only),
    path('admin_quest_page_view_only/<quest_id>', views.admin_quest_page_view_only),

    #Admin Edit questions
    path('admin_edit_fr_question/<question_id>', views.admin_edit_fr_question),
    path('admin_edit_mc_question/<question_id>', views.admin_edit_mc_question),

    #User Pages
    path('user_home/<ldap>/<project_id>', views.user_home),
    path('user_quest_page/<ldap>/<quest_id>', views.user_quest_page),
    path('user_project_page/<ldap>', views.user_project_page),
    path('new_user', views.new_user),
    path('user_login', views.user_login),

    






]
