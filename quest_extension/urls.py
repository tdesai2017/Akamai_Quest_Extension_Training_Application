from django.urls import path
from . import views
from django.conf.urls import url


urlpatterns = [
    #Decides what Question Admin wants to create
    path('mc-create-form/<ldap>/<quest_id>', views.get_mc_question_form),
    path('create_mc_question/<ldap>/<quest_id>', views.create_mc_question),



######################################


    path('fr-create-form/<ldap>/<quest_id>', views.get_fr_question_form),
    path('create_fr_question/<ldap>/<quest_id>', views.create_fr_question),

######################################



    #Admin Pages
    path('admin_home_editable/<ldap>/<project_id>', views.get_admin_home_editable),
    path('save_new_quest/<ldap>/<project_id>', views.save_new_quest),



######################################


    path('admin_quest_page_editable/<ldap>/<quest_id>', views.get_admin_quest_page_editable),
    path('delete_question/<ldap>/<quest_id>', views.delete_question),
    path('undo_delete_question/<ldap/<quest_id>', views.undo_delete_question),
    path('save_video/<ldap>/<quest_id>', views.save_video),
    path('delete_video/<ldap>/<quest_id>', views.delete_video), 





######################################


    path('admin_project_page/<ldap>', views.get_admin_project_page),
    path('add_new_project/<ldap>', views.add_new_project),


######################################


    path('admin_home_view_only/<ldap>/<project_id>', views.get_admin_home_view_only),

######################################


    path('admin_quest_page_view_only/<ldap>/<quest_id>', views.get_admin_quest_page_view_only),


######################################



    #Admin Edit questions
    path('admin_edit_fr_question/<ldap>/<question_id>', views.admin_edit_fr_question),

######################################


    path('admin_edit_mc_question/<ldap>/<question_id>', views.get_edit_mc_question),
    path('save_edit_mc_question/<ldap>/<question_id>', views.save_edit_mc_question),


######################################



    #User Pages
    path('user_home/<ldap>/<project_id>', views.get_user_home),


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
    path('change_password_request', views.change_password_request),
    path('go_back_to_login/<ldap>', views.go_back_to_login),

######################################
path('user_forgot_password/<ldap>', views.get_user_forgot_password),
path('new_password_sent/<ldap>', views.new_password_sent),

######################################

# path('admin_edit_project_description/<project_id>', views.get_admin_edit_project_description),
path('admin_update_project_description/<ldap>/<project_id>', views.admin_update_project_description),

###########################

path('user_info/<ldap>',views.get_user_info),
path('update_user_ldap/<ldap>', views.update_user_ldap),
path('update_user_first_name/<ldap>', views.update_user_first_name),
path('update_user_last_name/<ldap>', views.update_user_last_name),
path('update_user_email/<ldap>', views.update_user_email),
path('update_user_manager_ldap/<ldap>', views.update_user_manager_ldap),
path('update_user_director_ldap/<ldap>', views.update_user_director_ldap),
path('update_user_password/<ldap>', views.update_user_password),



##############################

path ('admin_project_info/<project_id>', views.get_admin_project_info),
path ('delete_project/<project_id>', views.delete_project),

##############################

path('admin_login', views.get_admin_login),
path('admin_login_to_account', views.admin_login_to_account),








    




]
