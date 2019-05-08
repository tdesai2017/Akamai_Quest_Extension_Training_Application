from django.urls import path
from . import views
from django.conf.urls import url


urlpatterns = [
    #Decides what Question Admin wants to create
    path('mc-create-form/<quest_id>', views.get_mc_question_form),
    path('create_mc_question/<quest_id>', views.create_mc_question),



######################################


    path('fr-create-form/<quest_id>', views.get_fr_question_form),
    path('create_fr_question/<quest_id>', views.create_fr_question),

######################################



    #Admin Pages
    path('admin_home_editable/<project_id>', views.get_admin_home_editable),
    path('save_new_quest/<project_id>', views.save_new_quest),



######################################


    path('admin_quest_page_editable/<quest_id>', views.get_admin_quest_page_editable),
    path('delete_question/<quest_id>', views.delete_question),
    path('undo_delete_question/<quest_id>', views.undo_delete_question),



######################################


    path('admin_project_page', views.get_admin_project_page),
    path('add_new_project', views.add_new_project),


######################################


    path('admin_home_view_only/<project_id>', views.get_admin_home_view_only),

######################################


    path('admin_quest_page_view_only/<quest_id>', views.get_admin_quest_page_view_only),


######################################



    #Admin Edit questions
    path('admin_edit_fr_question/<question_id>', views.admin_edit_fr_question),

######################################


    path('admin_edit_mc_question/<question_id>', views.get_edit_mc_question),
    path('save_edit_mc_question/<question_id>', views.save_edit_mc_question),


######################################



    #User Pages
    path('user_home/<ldap>/<project_id>', views.get_user_home),
    path('click_on_quest/<ldap>/<project_id>', views.click_on_quest),


######################################


    path('user_quest_page/<ldap>/<quest_id>', views.get_user_quest_page),
    path('validate_fr_question_response/<ldap>/<quest_id>', views.validate_fr_question_response),
    path('validate_mc_question_response/<ldap>/<quest_id>', views.validate_mc_question_response),



######################################


    path('user_project_page/<ldap>', views.get_user_project_page),
    path('user_logout/<ldap>', views.user_logout),
    path('add_user_project_page/<ldap>', views.add_user_project_page),
    path('remove_user_project/<ldap>', views.remove_user_project),


######################################


    path('new_user', views.get_new_user_page),
    path('add_new_user', views.add_new_user),


######################################


    path('user_login', views.get_user_login),
    path('user_login_to_account', views.user_login_to_account),



    






]
