from django.urls import path
from quest_extension import views
from django.conf.urls import url, include


app_name = 'quest'
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
    path('admin_update_project_description/<ldap>/<project_id>', views.admin_update_project_description),
    path('admin_update_project_name/<ldap>/<project_id>', views.admin_update_project_name),



######################################


    path('admin_quest_page_editable/<ldap>/<quest_id>', views.get_admin_quest_page_editable),
    path('delete_question/<ldap>/<quest_id>', views.delete_question),
    path('undo_delete_question/<ldap>/<quest_id>', views.undo_delete_question),
    path('save_video/<ldap>/<quest_id>', views.save_video),
    path('delete_video/<ldap>/<quest_id>', views.delete_video), 
    path('admin_update_quest_name/<ldap>/<quest_id>', views.update_quest_name),
    path('admin_update_quest_description/<ldap>/<quest_id>', views.update_quest_description),
    
######################################

    path('admin_quest_settings_editable/<ldap>/<quest_id>', views.get_admin_quest_settings_editable),
    path('update_quest_points_earned/<ldap>/<quest_id>', views.update_quest_points_earned),
    path('update_quest_path_number/<ldap>/<quest_id>', views.update_quest_path_number),
    path('delete_quest/<ldap>/<quest_id>', views.delete_quest),
######################################


path ('admin_quest_settings_view_only/<ldap>/<quest_id>', views.get_admin_quest_settings_view_only),


######################################


    path('admin_project_page/<ldap>', views.get_admin_project_page),
    path('add_new_project/<ldap>', views.add_new_project),
    path('join_project/<ldap>', views.join_project),


######################################


    path('admin_home_view_only/<ldap>/<project_id>', views.get_admin_home_view_only),

######################################


    path('admin_quest_page_view_only/<ldap>/<quest_id>', views.get_admin_quest_page_view_only),


######################################



    #Admin Edit questions
    path('admin_edit_fr_question/<ldap>/<question_id>', views.get_admin_edit_fr_question),
    path('save_edit_fr_question/<ldap>/<question_id>', views.save_admin_edit_fr_question),


######################################


    path('admin_edit_mc_question/<ldap>/<question_id>', views.get_admin_edit_mc_question),
    path('save_edit_mc_question/<ldap>/<question_id>', views.save_admin_edit_mc_question),


######################################



    #User Pages
    path('user_home/<ldap>/<project_id>', views.get_user_home),


######################################


    path('user_quest_page/<ldap>/<quest_id>', views.get_user_quest_page),
    # path('validate_fr_question_response/<ldap>/<quest_id>', views.validate_fr_question_response),
    # path('validate_mc_question_response/<ldap>/<quest_id>', views.validate_mc_question_response),
    path('validate_user_input/<ldap>/<quest_id>', views.validate_user_input),


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
    path('user_change_password_request', views.user_change_password_request),
    path('go_back_to_login/<ldap>', views.go_back_to_login),

######################################
path('user_forgot_password/<ldap>', views.get_user_forgot_password),
path('new_password_sent/<ldap>', views.new_password_sent),

######################################



path('user_settings_info/<ldap>',views.get_user_settings_info),
path('update_user_ldap/<ldap>', views.update_user_ldap),
path('update_user_first_name/<ldap>', views.update_user_first_name),
path('update_user_last_name/<ldap>', views.update_user_last_name),
path('update_user_email/<ldap>', views.update_user_email),
path('update_user_password/<ldap>', views.update_user_password),



##############################

path('admin_login', views.get_admin_login),
path('admin_login_to_account', views.admin_login_to_account),
path('admin_change_password_request', views.admin_change_password_request),


##############################

 path('new_admin', views.get_new_admin_page),
 path('add_new_admin', views.add_new_admin),

 ##############################
path('admin_forgot_password/<ldap>', views.get_admin_forgot_password),
path('admin_new_password_sent/<ldap>', views.admin_new_password_sent),
path('admin_go_back_to_login/<ldap>', views.admin_go_back_to_login),



##############################

path ('admin_project_settings_view_only/<ldap>/<project_id>', views.get_admin_project_settings_view_only),
path ('admin_project_settings_editable/<ldap>/<project_id>', views.get_admin_project_settings_editable),

path ('delete_project/<ldap>/<project_id>', views.delete_project),
path('update_project_random_phrase/<ldap>/<project_id>', views.update_random_phrase),
path('update_project_admin_pin/<ldap>/<project_id>', views.update_admin_pin),
path('remove_as_admin/<ldap>/<project_id>', views.remove_as_admin),
path('add_team/<ldap>/<project_id>', views.add_team),
path('remove_all_users/<ldap>/<project_id>', views.remove_all_users),
path('delete_team/<ldap>/<project_id>', views.delete_team),

##############################


path('admin_settings_info/<ldap>',views.get_admin_settings_info),
path('update_admin_ldap/<ldap>', views.update_admin_ldap),
path('update_admin_first_name/<ldap>', views.update_admin_first_name),
path('update_admin_last_name/<ldap>', views.update_admin_last_name),
path('update_admin_email/<ldap>', views.update_admin_email),
path('update_admin_password/<ldap>', views.update_admin_password),

##############################

path('admin_project_info_page/<ldap>/<project_id>', views.get_admin_project_info_page),
path('search_above/<ldap>/<project_id>', views.search_above),
path('search_below/<ldap>/<project_id>', views.search_below), 
path('search_at/<ldap>/<project_id>', views.search_at),
path('search_by_user_ldap/<ldap>/<project_id>', views.search_by_user_ldap),
path('search_all_users/<ldap>/<project_id>', views.search_all_users),
path('search_completed_users/<ldap>/<project_id>', views.search_completed_users),
path('search_not_completed_users/<ldap>/<project_id>', views.search_not_completed_users),


]
