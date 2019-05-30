from django.shortcuts import render
from django.http import HttpResponse
from quest_extension.models import *
from .forms import *
from django.http import HttpResponseRedirect
from django.utils.text import slugify
from django.utils.http import urlencode
from random import shuffle
from django.core.validators import validate_email 
from django.contrib import messages
from datetime import datetime
import copy
from quest_extension.logic import *
from django.core.mail import send_mail
import random
import json
import hashlib



#Views

#For the creation of a FR question (not editing)
def get_fr_question_form(request, ldap, quest_id):

    current_quest = Quest.objects.get(id = quest_id)
    current_project = current_quest.project

    
    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')


    if not is_still_editable(current_project):
        messages.warning(request, 'Someone has joined the project, so you must re-enter it in the view only mode')
        return HttpResponseRedirect('/quest/admin_project_page/' + ldap)

    current_admin = Admin.objects.get(admin_ldap = ldap)
    question_form = QuestionForm()
    answer_form = CorrectAnswerForm()
    context = {'q_form' : question_form, 'ans_form' : answer_form, 'quest_id': quest_id, 'current_admin': current_admin}
    return render(request, 'quest_extension/fr_question_form.html', context)

def create_fr_question(request, ldap, quest_id):
    
    current_quest = Quest.objects.get(id = quest_id)
    current_project = current_quest.project

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    if not is_still_editable(current_project):
        messages.warning(request, 'Someone has joined the project, so you must re-enter it in the view only mode')
        return HttpResponseRedirect('/quest/admin_project_page/' + ldap)

    if request.method  == 'POST':
        question_form = QuestionForm(request.POST)
        answer_form = CorrectAnswerForm(request.POST)
        if question_form.is_valid() and answer_form.is_valid():
            messages.success(request, 'New question successfully created!')
            return save_fr_question(ldap, question_form, answer_form, quest_id)
    
    return HttpResponseRedirect('/quest/fr-create-form/' + ldap + '/' + str(quest_id))
    
    
######################################

#For the creation of a free response form (not editing)
def get_mc_question_form(request, ldap, quest_id):

    current_quest = Quest.objects.get(id = quest_id)
    current_project = current_quest.project

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')


    if not is_still_editable(current_project):
        messages.warning(request, 'Someone has joined the project, so you must re-enter it in the view only mode')
        return HttpResponseRedirect('/quest/admin_project_page/' + ldap)

    current_admin = Admin.objects.get(admin_ldap = ldap)
    question_form = QuestionForm()
    answer_form = RightAnswerForm()
    wrong_answer_form = WrongAnswerForm()
    context = {'q_form' : question_form, 'ans_form' : answer_form, 'wrong_answer_form' : wrong_answer_form, 'quest_id': quest_id, 'current_admin': current_admin}
    return render(request, 'quest_extension/mc_question_form.html', context)


def create_mc_question(request, ldap, quest_id):

    current_quest = Quest.objects.get(id = quest_id)
    current_project = current_quest.project

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    if not is_still_editable(current_project):
        messages.warning(request, 'Someone has joined the project, so you must re-enter it in the view only mode')
        return HttpResponseRedirect('/quest/admin_project_page/' + ldap)

    if request.method  == 'POST':
        question_form = QuestionForm(request.POST)
        answer_form = RightAnswerForm(request.POST)
        wrong_answer_form = WrongAnswerForm(request.POST)
        if question_form.is_valid() and answer_form.is_valid() and wrong_answer_form.is_valid():
            messages.success(request, 'New question successfully created!')
            return save_mc_question(ldap, question_form, answer_form, wrong_answer_form, quest_id)
        
    return HttpResponseRedirect('/quest/mc-create-form/' + ldap + '/' + str(quest_id))


######################################


def get_admin_home_editable(request, ldap, project_id): 

    current_project = Project.objects.get(id = project_id)    

    if not (validate_admin_access(request, ldap) and can_admin_access_project(ldap, project_id)):
        return HttpResponseRedirect('/quest/admin_login')

    if not is_still_editable(current_project):
        messages.warning(request, 'Someone has joined the project, so you must re-enter it in the view only mode')
        return HttpResponseRedirect('/quest/admin_project_page/' + ldap)

    #I start a session here so that when we go "back" from pages that are common to both
    #editable and view only pages, we will know if we were in an editable or view_only
    #page
    request.session['view_or_editable'] = 'editable'

        
    current_admin = Admin.objects.get(admin_ldap = ldap)
    quests = Quest.objects.filter(project = current_project).order_by('quest_path_number')
    quest_form = QuestForm()
    #Only display all_teams_and_points in template if this project does in face use teams
    all_teams_and_points = get_team_points_format(current_project)

    
    context = {'quests':quests, 
    'quest_form': quest_form, 
    'current_project': current_project, 
    'current_admin': current_admin, 
    'all_teams_and_points': all_teams_and_points
    }
    return render(request, 'quest_extension/admin_home_editable.html', context)

def save_new_quest(request, ldap, project_id): 

    current_project = Project.objects.get(id = project_id)

    if not (validate_admin_access(request, ldap) and can_admin_access_project(ldap, project_id)):
        return HttpResponseRedirect('/quest/admin_login')

    if not is_still_editable(current_project):
        messages.warning(request, 'Someone has joined the project, so you must re-enter it in the view only mode')
        return HttpResponseRedirect('/quest/admin_project_page/' + ldap)

    if request.method == 'POST':
        post_request = request.POST
        print (post_request)
        quest_form = QuestForm(post_request)
        #Two quests cannot have the same path and paths must be greater than 0
        all_quests_in_current_project = Quest.objects.filter(project = current_project)
        all_paths_in_current_project = [quest.quest_path_number for quest in all_quests_in_current_project]
        if int(post_request['quest_path_number']) > 0 and int(post_request['quest_path_number']) not in all_paths_in_current_project:
            print('I am here 1')
            if quest_form.is_valid():
                print('I am here 2')
                temp = quest_form.save(commit=False)
                temp.quest_description = post_request['quest_description']
                temp.project = current_project
                temp.save()
                messages.success(request, 'New quest added successfully!')

                # If a user has no current quest for a certain project since the admin never created a quest with path 1 until
                # now, the user's current quest will be updated here to the inputted quest with id = 1
                all_users_without_current_quests = UserProject.objects.filter(project = current_project, current_quest= None)
                if int(post_request['quest_path_number']) == 1 and len(all_users_without_current_quests) > 0:
                    print('Yes we made it here at least', len(all_users_without_current_quests))
                    for userproject in all_users_without_current_quests:
                        userproject.current_quest = temp
                        userproject.save()
        else:
            messages.error(request, 'Duplicate or invalid path number!')


    return HttpResponseRedirect('/quest/admin_home_editable/' + ldap + '/' + str(project_id))




def admin_update_project_description(request, ldap, project_id):

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    current_project = Project.objects.get(id = project_id)

    if request.method == 'POST':
        post_request = request.POST
        updated_project_description = post_request['project_description']
        current_project.project_description = updated_project_description
        current_project.save()
        messages.success(request, 'Description successfully updated!')



    return redirect_to_correct_home_page(request.session['view_or_editable'], ldap, project_id)




def admin_update_project_name (request, ldap, project_id):

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    current_project = Project.objects.get(id = project_id)

    if request.method == 'POST':
        post_request = request.POST
        updated_project_name = post_request['project_name']
        current_project.project_name = updated_project_name
        current_project.save()
        messages.success(request, 'Name successfully updated!')


    return redirect_to_correct_home_page(request.session['view_or_editable'], ldap, project_id)
    
######################################


def get_admin_home_view_only(request, ldap,  project_id): 

    request.session['view_or_editable'] = 'view'


    if not (validate_admin_access(request, ldap) and can_admin_access_project(ldap, project_id)):
        return HttpResponseRedirect('/quest/admin_login')

    current_admin = Admin.objects.get(admin_ldap = ldap)
    current_project = Project.objects.get(id = project_id)
    quests = Quest.objects.filter(project = current_project).order_by('quest_path_number')
    all_teams_and_points = get_team_points_format(current_project)

    context = {'quests':quests,
     'current_project': current_project,
     'current_admin': current_admin,
      'all_teams_and_points': all_teams_and_points}
    return render(request, 'quest_extension/admin_home_view_only.html', context)

######################################

def get_admin_quest_page_editable(request, ldap, quest_id):

    if not (validate_admin_access(request, ldap) and can_admin_access_quest(ldap, quest_id)):
        return HttpResponseRedirect('/quest/admin_login')


    current_quest = Quest.objects.get(id = quest_id)
    current_project = current_quest.project
    if not is_still_editable(current_project):
        messages.warning(request, 'Someone has joined the project, so you must re-enter it in the view only mode')
        return HttpResponseRedirect('/quest/admin_project_page/' + ldap)

    current_admin = Admin.objects.get(admin_ldap = ldap)
    current_quest = Quest.objects.get(id = quest_id)
    current_project_id = current_quest.project.id
    list_of_questions = Question.objects.filter(quest = current_quest, deleted=False).order_by('time_modified')
    fr_input_form = TakeInFreeResponseForm()
    video_form = VideoForm()
    all_videos = Video.objects.filter(quest = current_quest)

    format = {}
    for question in list_of_questions:
        correct_answer = CorrectAnswer.objects.filter(question = question)
        wrong_answers = IncorrectAnswer.objects.filter(question = question)
        #This was the only way I could find that would allows us to join two independent model types 
        #(by converting them into lists and appending them)
        all_answers = []

        for answer in wrong_answers:
            all_answers.append(answer)

        for answer in correct_answer:
            all_answers.append(answer)

        shuffle(all_answers)
        #Combines wrong answers with correct answer
        format[question] = all_answers 

    context = {'current_quest': current_quest,
     'format': format,
     'fr_input_form': fr_input_form,
     'current_project_id': current_project_id,
     'video_form': video_form,
     'all_videos': all_videos, 
     'current_admin': current_admin    
     }
    return render(request, 'quest_extension/admin_quest_page_editable.html', context)


def delete_question(request, ldap, quest_id):

    if not (validate_admin_access(request, ldap) and can_admin_access_quest(ldap, quest_id)):
        return HttpResponseRedirect('/quest/admin_login')


    current_quest = Quest.objects.get(id = quest_id)
    current_project = current_quest.project
    if not is_still_editable(current_project):
        messages.warning(request, 'Someone has joined the project, so you must re-enter it in the view only mode')
        return HttpResponseRedirect('/quest/admin_project_page/' + ldap)

    if request.method == 'POST':
        post_request = request.POST
        current_question = Question.objects.get(id = post_request['deleted'])
        print (post_request)
        #We want to not let the time_modified increase, so we save it here and assign it to the question after we save it
        current_time_modified = copy.deepcopy(current_question.time_modified)
        current_question.deleted = True
        current_question.save()
        messages.success(request, 'Question successfully deleted!')
        Question.objects.filter(id = post_request['deleted']).update(time_modified = current_time_modified)

    return HttpResponseRedirect('/quest/admin_quest_page_editable/' + ldap + '/' + str(quest_id))

def undo_delete_question(request, ldap, quest_id):

    if not (validate_admin_access(request, ldap) and can_admin_access_quest(ldap, quest_id)):
        return HttpResponseRedirect('/quest/admin_login')


    current_quest = Quest.objects.get(id = quest_id)
    current_project = current_quest.project
    if not is_still_editable(current_project):
        messages.warning(request, 'Someone has joined the project, so you must re-enter it in the view only mode')
        return HttpResponseRedirect('/quest/admin_project_page/' + ldap)

    if request.method == 'POST':        
        if Question.objects.filter(quest = current_quest, deleted = True):
            object_to_reappear = Question.objects.filter(quest = current_quest, deleted = True).latest('delete_time')
            #We want to not let the time_modified increase, so we save it here and assign it to the question after we save it
            object_to_reappear_id = object_to_reappear.id
            current_time_modified = copy.deepcopy(object_to_reappear.time_modified)
            object_to_reappear.deleted = False
            object_to_reappear.save()
            messages.success(request, 'Successful Undo!')
            Question.objects.filter(id = object_to_reappear_id).update(time_modified = current_time_modified)

    return HttpResponseRedirect('/quest/admin_quest_page_editable/' + ldap + '/' + str(quest_id))


def save_video(request, ldap, quest_id):

    if not (validate_admin_access(request, ldap) and can_admin_access_quest(ldap, quest_id)):
        return HttpResponseRedirect('/quest/admin_login')

    current_quest = Quest.objects.get(id = quest_id)
    
    if request.method == 'POST': 
        post_request = request.POST
        video_form = VideoForm(post_request)
        print(video_form)
        if video_form.is_valid():
            temp = video_form.save(commit=False)   
            url = post_request['video_url']
            if "v=" not in url or len(url) <= 2:
                    return HttpResponseRedirect('/quest/admin_quest_page_editable/' + ldap + '/' + str(quest_id))

            video_identifier = url[url.index('v=') + 2:]
            temp.video_url = video_identifier
            temp.quest = current_quest
            temp.save()
            messages.success(request, 'Video successfully added!')

    return redirect_to_correct_quest_page(request.session['view_or_editable'], ldap, quest_id)

def delete_video(request, ldap, quest_id):

    if not (validate_admin_access(request, ldap) and can_admin_access_quest(ldap, quest_id)):
        return HttpResponseRedirect('/quest/admin_login')

    if request.method == 'POST': 
        post_request = request.POST
        video_id = post_request['delete']
        video_to_delete = Video.objects.get(id = video_id)
        print("YOU ARE HERE", video_to_delete)
        video_to_delete.delete()
        messages.success(request, 'Video successfully deleted!')
            
    return redirect_to_correct_quest_page(request.session['view_or_editable'], ldap, quest_id)

def update_quest_name(request, ldap, quest_id):

    if not (validate_admin_access(request, ldap) and can_admin_access_quest(ldap, quest_id)):
        return HttpResponseRedirect('/quest/admin_login')

    current_quest = Quest.objects.get(id = quest_id)

    if request.method == 'POST': 
            post_request = request.POST
            updated_quest_name = post_request['quest_name']
            current_quest.quest_name = updated_quest_name
            current_quest.save()  
            messages.success(request, 'Name successfully updated!')


    return redirect_to_correct_quest_page(request.session['view_or_editable'], ldap, quest_id)



def update_quest_description(request, ldap, quest_id):

    if not (validate_admin_access(request, ldap) and can_admin_access_quest(ldap, quest_id)):
        return HttpResponseRedirect('/quest/admin_login')

    current_quest = Quest.objects.get(id = quest_id)
    

    if request.method == 'POST': 
            post_request = request.POST
            updated_quest_description = post_request['quest_description']
            current_quest.quest_description = updated_quest_description
            current_quest.save() 
            messages.success(request, 'Description successfully updated!')
               

    return redirect_to_correct_quest_page(request.session['view_or_editable'], ldap, quest_id)


######################################

def get_admin_quest_settings_editable(request, ldap, quest_id):

    if not (validate_admin_access(request, ldap) and can_admin_access_quest(ldap, quest_id)):
        return HttpResponseRedirect('/quest/admin_login')

    current_quest = Quest.objects.get(id = quest_id)
    current_project = current_quest.project
    if not is_still_editable(current_project):
        messages.warning(request, 'Someone has joined the project, so you must re-enter it in the view only mode')
        return HttpResponseRedirect('/quest/admin_project_page/' + ldap)

    current_admin = Admin.objects.get(admin_ldap = ldap)
    context = {'current_quest': current_quest, 'current_admin': current_admin}

    return render (request, 'quest_extension/admin_quest_settings_editable.html', context)

def update_quest_points_earned(request, ldap, quest_id):

    if not (validate_admin_access(request, ldap) and can_admin_access_quest(ldap, quest_id)):
        return HttpResponseRedirect('/quest/admin_login')

    current_admin = Admin.objects.get(admin_ldap = ldap)
    
    current_quest = Quest.objects.get(id = quest_id)
    current_project = current_quest.project
    if not is_still_editable(current_project):
        messages.warning(request, 'Someone has joined the project, so you must re-enter it in the view only mode')
        return HttpResponseRedirect('/quest/admin_project_page/' + ldap)

    if request.method == 'POST':
        post_request = request.POST
        quest_points_earned_input = post_request['quest_points_earned']
        current_quest.quest_points_earned = quest_points_earned_input
        current_quest.save()
        messages.success(request, 'Quest points successfully updated!')


    return HttpResponseRedirect('/quest/admin_quest_settings_editable/' + current_admin.admin_ldap + '/' + str(quest_id))

def update_quest_path_number(request, ldap, quest_id):

    if not (validate_admin_access(request, ldap) and can_admin_access_quest(ldap, quest_id)):
        return HttpResponseRedirect('/quest/admin_login')

    current_admin = Admin.objects.get(admin_ldap = ldap)
    current_quest = Quest.objects.get(id = quest_id)
    all_quest_path_numbers_in_project = Quest.objects.filter(project = current_quest.project).values_list('quest_path_number', flat=True)
    
    current_project = current_quest.project
    if not is_still_editable(current_project):
        messages.warning(request, 'Someone has joined the project, so you must re-enter it in the view only mode')
        return HttpResponseRedirect('/quest/admin_project_page/' + ldap)

    if request.method == 'POST':
        post_request = request.POST
        quest_path_number_input = post_request['quest_path_number']
        if int(quest_path_number_input) not in all_quest_path_numbers_in_project and int(quest_path_number_input) > 0:
            current_quest.quest_path_number = quest_path_number_input
            current_quest.save()
            messages.success(request, 'Quest path number successfully updated!')
        else:
            messages.error(request, 'Please Input a valid path number (greater than 0 and no duplicate path numbers)')
        


    return HttpResponseRedirect('/quest/admin_quest_settings_editable/' + current_admin.admin_ldap + '/' + str(quest_id))


def delete_quest(request, ldap, quest_id):

    if not (validate_admin_access(request, ldap) and can_admin_access_quest(ldap, quest_id)):
        return HttpResponseRedirect('/quest/admin_login')

    current_quest = Quest.objects.get(id = quest_id)
    current_project = current_quest.project
    if not is_still_editable(current_project):
        messages.warning(request, 'Someone has joined the project, so you must re-enter it in the view only mode')
        return HttpResponseRedirect('/quest/admin_project_page/' + ldap)

    current_admin = Admin.objects.get(admin_ldap = ldap)
    project_id = current_quest.project.id
    if request.method == 'POST':
        current_quest.delete()

    messages.success(request, 'Quest "' + current_quest.quest_name + '" successfully deleted!')
    return HttpResponseRedirect('/quest/admin_home_editable/' + current_admin.admin_ldap + '/' + str(project_id))
######################################

def get_admin_quest_settings_view_only(request, ldap, quest_id):

    if not (validate_admin_access(request, ldap) and can_admin_access_quest(ldap, quest_id)):
        return HttpResponseRedirect('/quest/admin_login')

    current_quest = Quest.objects.get(id = quest_id)
    current_admin = Admin.objects.get(admin_ldap = ldap)
    context = {'current_quest': current_quest, 'current_admin': current_admin}

    return render (request, 'quest_extension/admin_quest_settings_view_only.html', context)


######################################

def get_admin_quest_page_view_only(request, ldap, quest_id):

    if not (validate_admin_access(request, ldap) and can_admin_access_quest(ldap, quest_id)):
        return HttpResponseRedirect('/quest/admin_login')

    current_admin = Admin.objects.get(admin_ldap = ldap)
    current_quest = Quest.objects.get(id = quest_id)
    current_project_id = current_quest.project.id
    list_of_questions = Question.objects.filter(quest = current_quest, deleted=False).order_by('time_modified')
    fr_input_form = TakeInFreeResponseForm()
    all_videos = Video.objects.filter(quest = current_quest)
    video_form = VideoForm()


    format = {}
    for question in list_of_questions:
        correct_answer = CorrectAnswer.objects.filter(question = question)
        wrong_answers = IncorrectAnswer.objects.filter(question = question)
        #This was the only way I could find that would allows us to join two independent model types 
        #(by converting them into lists and appending them)
        all_answers = []

        for answer in wrong_answers:
            all_answers.append(answer)

        for answer in correct_answer:
            all_answers.append(answer)

        shuffle(all_answers)
        #Combines wrong answers with correct answer
        format[question] = all_answers 

    context = {'current_quest': current_quest,
    'format': format,
    'fr_input_form': fr_input_form,
    'current_project_id': current_project_id,
    'all_videos': all_videos,
    'current_admin': current_admin,
    'video_form': video_form}
    return render(request, 'quest_extension/admin_quest_page_view_only.html', context)

######################################

def get_user_home(request, ldap, project_id):

    if not validate_user_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    user = User.objects.get(user_ldap= ldap)
    current_project = Project.objects.get(id = project_id)
    current_user_project_object = UserProject.objects.get(user = user, project = current_project)
    quests = Quest.objects.filter(project = current_project).order_by('quest_path_number')
    current_user_project_team = current_user_project_object.team
    all_teams_and_points = get_team_points_format(current_project)
    #Points information for teams
    

    context = {'quests':quests, 
                'user': user, 
                'current_project': current_project, 
                'current_user_project_object': current_user_project_object, 
                'current_user_project_team': current_user_project_team,
                'all_teams_and_points': all_teams_and_points}
    return render(request, 'quest_extension/user_home.html', context)


######################################

def get_user_quest_page(request, ldap, quest_id):

    if not validate_user_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    current_quest = Quest.objects.get(id = quest_id)
    current_project_id = current_quest.project.id
    current_user = User.objects.get(user_ldap = ldap)
    current_project = current_quest.project
    all_videos = Video.objects.filter(quest = current_quest)
    current_user_project = UserProject.objects.get(user = current_user, project = current_project)

    # Ensures that you cannot move to a quest you are not allowed to be in just by altering the 
    # questions primary id in the url
    if (current_user_project.current_quest.quest_path_number < current_quest.quest_path_number):
        return HttpResponseRedirect('/quest/user_home/' + ldap + '/' + str(current_project_id))


    list_of_questions = Question.objects.filter(quest = current_quest, deleted=False).order_by('time_modified')
    fr_input_form = TakeInFreeResponseForm()
    
    #"question" also returns the primary id of the question
    have_correct_answer = CorrectlyAnsweredQuestion.objects.filter(userproject = current_user_project).values_list('question', flat = True)

    #Creates the format for the questions to be in
    format_2 = []
    for question in list_of_questions:
        correct_answer = CorrectAnswer.objects.filter(question = question)
        wrong_answers = IncorrectAnswer.objects.filter(question = question)
        all_answers = []
        correct_answer_2 = []

        format_2_tuple = (question, all_answers, correct_answer)

        for answer in wrong_answers:
            all_answers.append(answer)

        for answer in correct_answer:
            all_answers.append(answer)
            correct_answer_2.append(answer)
        

        shuffle(all_answers)
        #Combines wrong answers with correct answer
        format_2.append(format_2_tuple)

    #attempt to map quesitons to correct answers
    question_to_answers = {}
    for question in list_of_questions:
        correct_answers = CorrectAnswer.objects.filter(question = question, deleted = False)
        list_of_correct_answers = [ans.answer_text for ans in correct_answers]
        question_to_answers[question.id] = list_of_correct_answers
    question_to_answers = json.dumps(question_to_answers)


    context = {'current_quest': current_quest, 
            # 'fr_input_form': fr_input_form, 
            'ldap': ldap, 
            'current_project_id': current_project_id, 
            'have_correct_answer': have_correct_answer,
            'format_2': format_2,
            'all_videos': all_videos,
            'question_to_answers': question_to_answers}

    return render(request, 'quest_extension/user_quest_page.html', context)

# def validate_fr_question_response(request, ldap, question, user_answer):

#     if not validate_user_access(request, ldap):
#         return HttpResponseRedirect('/quest/user_login')

#     current_quest = Quest.objects.get(id = quest_id)
#     current_project = current_quest.project
#     current_user = User.objects.get(user_ldap = ldap)

#     if request.method == 'POST':
#         #When do I check here whether the form is valid
#         post_request = request.POST
#         user_answer = post_request['answer']
#         current_question = Question.objects.get(id = post_request['FR_response_id'])
#         correct_answers = CorrectAnswer.objects.filter(question = current_question)
#         current_user_project = UserProject.objects.get(user = current_user, project = current_project)

        
#         correct_answers_texts = []
#         for answer in correct_answers:
#             correct_answers_texts.append(answer.answer_text)

#         if user_answer in correct_answers_texts:
#             print("You are correct")
#             #Creates a new MODEL INSTANCE of CorrectlyAnswerQuestions
#             correctly_answered_question = CorrectlyAnsweredQuestion()
#             #Adds a new correctly answer question
#             correctly_answered_question.question = current_question
#             correctly_answered_question.userproject = current_user_project
#             correctly_answered_question.save()
#             go_to_next_quest(current_quest, current_user, current_project)
#         else:
#              messages.error(request, 'Sorry, that\'s not the right answer :(', extra_tags = str(current_question.id))

#     return HttpResponseRedirect('/quest/user_quest_page/' + ldap + '/' + str(quest_id))






def validate_user_input(request, ldap, quest_id):

    if not validate_user_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    if request.method == 'POST':
        post_request = request.POST
        print(post_request)
        for key, value in post_request.items():
            if 'answer' in key and post_request.getlist(key)[0] != '':
                question = Question.objects.get (id = key[key.index('_') + 1:])
                validate_question_response (request, ldap, question, post_request.getlist(key))

    return HttpResponseRedirect('/quest/user_quest_page/' + ldap + '/' + str(quest_id))


######################################

#For editing free response questions (not creating)
def get_admin_edit_fr_question(request, ldap, question_id):

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    current_question = Question.objects.get(id = question_id)
    current_quest = current_question.quest
    current_project = current_quest.project
    if not is_still_editable(current_project):
        messages.warning(request, 'Someone has joined the project, so you must re-enter it in the view only mode')
        return HttpResponseRedirect('/quest/admin_project_page/' + ldap)

    current_admin = Admin.objects.get(admin_ldap = ldap)
    current_questions_answers = CorrectAnswer.objects.filter(question = current_question)
    question_text_form = QuestionForm(initial={'question_text': current_question.question_text})

    all_answers = ""
    for answer in current_questions_answers:
        answer_text = answer.answer_text
        all_answers += (answer_text + " ")

    fr_answer_form = CorrectAnswerForm(initial={'answer_text': all_answers})

    print(current_question.question_type)
    context = {'current_question': current_question,
                'question_text_form': question_text_form,
                'fr_answer_form': fr_answer_form,
                'current_admin': current_admin}
    return render(request, 'quest_extension/admin_edit_fr_question.html', context)


def save_admin_edit_fr_question(request, ldap, question_id):

    current_question = Question.objects.get(id = question_id)

    current_quest = current_question.quest
    current_project = current_quest.project
    if not is_still_editable(current_project):
        messages.warning(request, 'Someone has joined the project, so you must re-enter it in the view only mode')
        return HttpResponseRedirect('/quest/admin_project_page/' + ldap)

    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        answer_form = CorrectAnswerForm(request.POST)
        quest_id = current_question.quest.id
        if question_form.is_valid() and answer_form.is_valid():
            timestamp = copy.deepcopy(current_question.time_modified)
            print(timestamp)
            current_question.deleted = True
            current_question.save()
            #If you want to undo the deletion of the previous version of the question, it will pop up back in
            #it's original place
            Question.objects.filter(id = question_id).update(time_modified = timestamp)
            messages.success(request, 'Question successfully updated!')
            return save_fr_question(ldap, question_form, answer_form, quest_id, timestamp)

    return HttpResponseRedirect('/quest/admin_edit_fr_question/' + ldap + '/' + str(question_id))





######################################
#For editing mc questions (not creating)
def get_admin_edit_mc_question(request, ldap, question_id):

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')


    current_question = Question.objects.get(id = question_id)
    current_quest = current_question.quest
    current_project = current_quest.project
    if not is_still_editable(current_project):
        messages.warning(request, 'Someone has joined the project, so you must re-enter it in the view only mode')
        return HttpResponseRedirect('/quest/admin_project_page/' + ldap)

    current_admin = Admin.objects.get(admin_ldap = ldap)
    correct_answers = CorrectAnswer.objects.filter(question = current_question)
    wrong_answers = IncorrectAnswer.objects.filter(question= current_question)
    question_text_form = QuestionForm(initial={'question_text': current_question.question_text})
    quest_id = current_question.quest.id

    all_correct_answers = ""
    for answer in correct_answers:
        answer_text = answer.answer_text
        all_correct_answers += (answer_text + "\n")

    all_wrong_answers = ""
    for answer in wrong_answers:
        answer_text = answer.answer_text
        all_wrong_answers += (answer_text + "\n")

    mc_correct_answer_form = RightAnswerForm(initial={'correct_choices': all_correct_answers})
    mc_wrong_answer_form = WrongAnswerForm(initial={'incorrect_choices': all_wrong_answers})

    current_question = Question.objects.get(id = question_id)
    print(current_question.question_type)
    context = {'current_question': current_question,
                'question_text_form': question_text_form,
                'mc_correct_answer_form': mc_correct_answer_form,
                'mc_wrong_answer_form': mc_wrong_answer_form,
                'quest_id': quest_id,
                'current_admin': current_admin}
    return render(request, 'quest_extension/admin_edit_mc_question.html', context)
    
def save_admin_edit_mc_question (request, ldap, question_id):

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')


    current_question = Question.objects.get(id = question_id)
    current_quest = current_question.quest
    current_project = current_quest.project
    if not is_still_editable(current_project):
        messages.warning(request, 'Someone has joined the project, so you must re-enter it in the view only mode')
        return HttpResponseRedirect('/quest/admin_project_page/' + ldap)

    quest_id = current_question.quest.id
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        answer_form = RightAnswerForm(request.POST)
        wrong_answer_form = WrongAnswerForm(request.POST)
        if question_form.is_valid() and answer_form.is_valid() and wrong_answer_form.is_valid():
            timestamp = copy.deepcopy(current_question.time_modified)
            print(timestamp)
            current_question.deleted = True
            current_question.save()
            #If you want to undo the deletion of the previous version of the question, it will pop up back in
            #it's original place
            Question.objects.filter(id = question_id).update(time_modified = timestamp)
            messages.success(request, 'Question successfully updated!')
            return save_mc_question(ldap, question_form, answer_form, wrong_answer_form, quest_id, timestamp)

    return HttpResponseRedirect('/quest/admin_edit_mc_question/' + ldap + '/' + str(question_id))

######################################

def get_admin_project_page(request, ldap):

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')
    
    #This session will only last while a user is in either an editable or non-editable path
    if 'view_or_editable' in request.session:
        del request.session['view_or_editable']

    project_form = ProjectForm()
    current_admin = Admin.objects.get(admin_ldap = ldap)
    #Only include projects that there is a AdminProject link for
    list_of_projects = AdminProject.objects.filter(admin = current_admin).values_list('project', flat=True)
    list_of_projects = Project.objects.filter(pk__in=list_of_projects)
    

    context = {'project_form': project_form, 'list_of_projects': list_of_projects, 'current_admin': current_admin}
    return render(request, 'quest_extension/admin_project_page.html', context)

def add_new_project(request, ldap):

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    current_admin = Admin.objects.get(admin_ldap = ldap)
    if request.method == 'POST':
        post_request = request.POST
        # form was submitted
        project_form = ProjectForm(request.POST)


        #No duplicates allowed for security purposes
        random_phrase_input = post_request['project_random_phrase']
        is_new_random_phrase = random_phrase_input not in Project.objects.all().values_list('project_random_phrase', flat=True) 
        admin_pin_input = post_request['project_admin_pin']
        is_new_admin_pin = admin_pin_input not in Project.objects.all().values_list('project_admin_pin', flat=True) 
        if not is_new_random_phrase:
            messages.error(request, 'Please use a different random phrase for security purposes')
        if not is_new_admin_pin:
            messages.error(request, 'Please use a different admin pin for security purposes')

        print(post_request)
        if project_form.is_valid():
            temp = project_form.save(commit=False)
            temp.project_editable = True
            temp.project_description = post_request['project_description']
            
            teams = []
            #if the project will have teams, detail this in the project model
            if 'teams' in post_request.keys() and post_request['teams'] != '':
                teams = post_request['teams'].split('\n')
                #Removes blank teams
                teams = [x for x in teams if len(x.strip())>0]
                list_of_teams = [x.strip() for x in teams]
                
                #checks if there are duplicates team names, which is not allowed

                if len(list_of_teams) != len (set(list_of_teams)):
                    messages.error(request, 'You cannot have teams with the same name')
                    return HttpResponseRedirect('/quest/admin_project_page/' + ldap)
                
                temp.project_has_teams = True

                
            temp.save() #saves proejct
            messages.success(request, 'You have successfully created a new project!')
            project_id = temp.id  
            current_project = Project.objects.get(id = project_id) 

            for team_name in teams:
                team_name = str(team_name).strip()
                team_object = Team()
                team_object.project = current_project
                team_object.team_name = team_name
                team_object.save() #saves teams
                
            print
            #Creates a new AdminProject
            new_admin_project = AdminProject()
            new_admin_project.admin = current_admin
            new_admin_project.project = current_project
            new_admin_project.save() # saves AdminProject
        
    
    return HttpResponseRedirect('/quest/admin_project_page/' + ldap)

def join_project(request, ldap):

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    current_admin = Admin.objects.get(admin_ldap = ldap)
    if request.method == 'POST':
        post_request = request.POST
        input_pin = post_request['project_admin_pin']
        input_name = post_request['project_name']
        list_of_admins_projects = AdminProject.objects.filter(admin = current_admin).values_list('project', flat = True)
        list_of_admins_projects = Project.objects.filter(pk__in=list_of_admins_projects)

        #To join a project, it cannot already be one you admin, and it must also exist
        if Project.objects.filter(project_admin_pin = input_pin):
            project_to_join = Project.objects.get(project_admin_pin = input_pin)
            project_name = project_to_join.project_name
            #We are further validating that they can become an admin of this project
            #Because they must also know the name of it
            if project_to_join in list_of_admins_projects and project_name == input_name:
                print (list_of_admins_projects)
                messages.error(request, 'You cannot join a project that you are already a part of')
                return HttpResponseRedirect('/quest/admin_project_page/' + ldap)

            elif project_name == input_name:
                new_admin_project = AdminProject()
                new_admin_project.admin = current_admin
                new_admin_project.project = project_to_join
                new_admin_project.save()
                messages.success(request, 'New project has been added!')


            else:
                messages.error(request, 'Invalid Name or Admin Pin')
        else:
                messages.error(request, 'Invalid Name or Admin Pin') 


    return HttpResponseRedirect('/quest/admin_project_page/' + ldap)
 




    
######################################
def get_user_project_page(request, ldap):

    if not validate_user_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    current_user = User.objects.get(user_ldap = ldap)
    user_projects = [user_project.project for user_project in UserProject.objects.filter(user = current_user)]
    user_project_ids = [project.id for project in user_projects]
    all_other_projects = [project for project in Project.objects.all() if project.id not in user_project_ids]
    add_new_project_form = AddNewProjectForm()

    context = {'current_user': current_user,
     'user_projects': user_projects,
      'all_other_projects': all_other_projects,
      'add_new_project_form': add_new_project_form}
    return render(request, 'quest_extension/user_project_page.html', context)


def user_logout(request, ldap):

    if not validate_user_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    if request.method == 'POST':
        del request.session['current_user_ldap']
        return HttpResponseRedirect('/quest/user_login')

    return HttpResponseRedirect('/quest/user_project_page/' + ldap)


def add_user_project_page(request, ldap):

    if not validate_user_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    current_user = User.objects.get(user_ldap = ldap)

    if request.method == 'POST':
        post_request = request.POST
        inputted_random_phrase = post_request['random_phrase']

        # This is a list of the projects you are already a part of
        list_of_user_projects = UserProject.objects.filter(user = current_user).values_list('project', flat=True)
        list_of_user_projects = Project.objects.filter(pk__in=list_of_user_projects)

        if Project.objects.filter(project_random_phrase = inputted_random_phrase):
            project_requested = Project.objects.get(project_random_phrase = inputted_random_phrase)
            has_teams = project_requested.project_has_teams
            if has_teams:
                teams_in_current_project = Team.objects.filter(project = project_requested)

            #If user did not add a team in their request to join the project
            if has_teams and post_request['team'] not in teams_in_current_project.values_list('team_name', flat=True):
                print (teams_in_current_project.values_list('team_name', flat=True), post_request['team'])
                messages.error(request, 'Please include a valid team name!')
                return HttpResponseRedirect('/quest/user_project_page/' + ldap)
            
            

            #If you're not already a part of this project
            if project_requested not in list_of_user_projects:
                new_user_project = UserProject()
                new_user_project.user = User.objects.get(user_ldap = ldap)
                new_user_project.project = project_requested
                if has_teams:
                    team_requested_for = Team.objects.get(team_name = post_request['team'], project = project_requested)
                    new_user_project.team = team_requested_for

                #Decides what quest the user will begin on (not neccessary since now you can't edit a project after a user joins however - see other comment above)
                if len(Quest.objects.filter(project = project_requested, quest_path_number = 1)) == 1:
                    new_user_project.current_quest = Quest.objects.get(project = project_requested, quest_path_number = 1)
                else:
                    new_user_project.current_quest = None

                #If we want to implement this later, we can make sure users can only join projects where
                #there is already a quest with quest_path_number == 1
                new_user_project.save() 
                #Since a user joined, the admin can no longer change the quest
                project_requested.project_editable = False
                project_requested.save()
                messages.success(request, 'Successfully joined "' + project_requested.project_name + '"!')
            else:
                messages.error(request, 'You are already part of this project!')
        else:
            messages.error(request, 'Please input a valid random phrase!')

    
    return HttpResponseRedirect('/quest/user_project_page/' + ldap)

def remove_user_project(request, ldap):

    if not validate_user_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    current_user = User.objects.get(user_ldap = ldap)
    
    if request.method == 'POST':
        post_request = request.POST
        #We aren't actually deleting the project, don't worry
        project_to_delete = Project.objects.get(id = post_request['remove_project'])
        current_user_project = UserProject.objects.get(project = project_to_delete, user = current_user )

        user_project_to_delete = UserProject.objects.get(user = current_user, project= project_to_delete)
        user_project_to_delete.delete()
        
        quests = Quest.objects.filter(project = project_to_delete)
        questions = Question.objects.filter(quest__in= quests)
        correctly_answered_questions = CorrectlyAnsweredQuestion.objects.filter(userproject = current_user_project, question__in = questions)
        correctly_answered_questions.delete()
        
        #If no users are on this project anymore, you can once again edit the project
        if len(UserProject.objects.filter(project = project_to_delete)) == 0:
            project_to_delete.project_editable = True
            project_to_delete.save()


        return HttpResponseRedirect('/quest/user_project_page/' + ldap)
    return HttpResponseRedirect('/quest/user_project_page/' + ldap)

######################################


def get_new_user_page(request):

    user_form = UserForm()
    context = {'user_form': user_form}
    return render(request, 'quest_extension/new_user.html', context)

def add_new_user(request):
    if request.method == 'POST':
        post_request = request.POST
        retyped_password = make_hash(post_request['retyped_password'])
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            temp = user_form.save(commit=False)
            email = temp.user_email
            user_ldap = temp.user_ldap
            user_password = temp.user_password
            temp.user_password = make_hash(user_password)
            try:
                validate_email(email)
                valid_email = True
            except:
                valid_email = False
                messages.error(request, 'Please input a valid email')
                return HttpResponseRedirect('/quest/new_user') 

            valid_password = (retyped_password == temp.user_password)
            is_new_ldap = user_ldap not in User.objects.all().values_list('user_ldap', flat=True) 
            print(User.objects.all().values_list('user_ldap', flat=True) )
            if valid_email and is_new_ldap and valid_password:
                temp.save()
                messages.success(request, 'Your new account was created!')
                return HttpResponseRedirect('/quest/user_login')
            if not is_new_ldap:
                messages.error(request, 'There is already an account associated with this LDAP')
            if not valid_password:
                messages.error(request, 'Your Password and Retyped Password do not match')

    return HttpResponseRedirect('/quest/new_user')

######################################

def get_user_login(request):
    #If you every reach this page, any current user sessions should be deleted so that you cannot skip
    #into quests
    if 'current_user_ldap' in request.session:
        del request.session['current_user_ldap']

    # if 'current_admin_ldap' in request.session:
    #     del request.session['current_admin_ldap']

    login_form = LoginForm()
    context = {'login_form': login_form}
    return render(request, 'quest_extension/user_login.html', context)

def user_login_to_account(request):
    if request.method == 'POST':
        post_request = request.POST
        ldap = post_request['ldap']
        password = make_hash(post_request['password'])
        print (post_request)

        if User.objects.filter(user_ldap = ldap):
            #If incorrect password
            if not User.objects.get(user_ldap = ldap).user_password == password:
                messages.error(request, 'Invalid Password')
            #If correct password for ldap - creates a session for the user
            else: 
                request.session['current_user_ldap'] = post_request['ldap']
                return HttpResponseRedirect('/quest/user_project_page/' + request.session['current_user_ldap'])
        #If LDAP is not associated with an account
        else:
            messages.error(request, 'There is no user account associated with this LDAP')
    
    return HttpResponseRedirect('/quest/user_login')


def user_change_password_request(request):
    if request.method == 'POST':
        post_request = request.POST
        ldap = post_request['ldap']

        #only proceed if there is a user with this ldap
        if not User.objects.filter(user_ldap = ldap):
            messages.error(request, 'There is no user account with this ldap')
            return HttpResponseRedirect('/quest/user_login')
        
        else:
            current_user = User.objects.get(user_ldap = ldap)
            pin = str(random.randint(99999, 999999))
            current_user.user_reset_password_pin = pin
            current_user.save()
            message_body = ('Hi ' + current_user.user_first_name + '. We have just recieved notice that you requested ' +
            'to create a new password! Your six digit pin is ' + str(pin))
            send_mail(
            'Password Reset',
            message_body,
            'icet.tushar@gmail.com', #This will have to change once we deploy this on a remote server
            [current_user.user_email],
            fail_silently=False,
            )
            print('MAIL SENT')
            return HttpResponseRedirect('/quest/user_forgot_password/' + ldap)
    
        return HttpResponseRedirect('/quest/user_login')





####################################

def get_user_forgot_password(request, ldap):
    forgot_password_form = ForgotPasswordForm()
    context = {'forgot_password_form': forgot_password_form, 'ldap': ldap}
    return render(request, 'quest_extension/user_forgot_password.html', context)

def new_password_sent(request, ldap):
    current_user = User.objects.get(user_ldap = ldap)
    if request.method == 'POST':
        forgot_password_form = ForgotPasswordForm(request.POST)
        if forgot_password_form.is_valid():
            pin = forgot_password_form.cleaned_data['pin']
            new_password = make_hash(forgot_password_form.cleaned_data['new_password'])
            retype_new_password = make_hash(forgot_password_form.cleaned_data['retype_new_password'])

            if (current_user.user_reset_password_pin != pin):
                messages.error(request,'Pin does not match the sent pin')
                return HttpResponseRedirect ('/quest/user_forgot_password/' + ldap)
            elif (new_password != retype_new_password):
                messages.error(request, 'Your Passwords do not match')
                return HttpResponseRedirect ('/quest/user_forgot_password/' + ldap)
            else:
                current_user.user_password = new_password
                #By setting this value to none as soon as possible, it leaves a very small window for
                #an intruder to try guessing the users pin
                current_user.user_reset_password_pin = None
                current_user.save()
                messages.success(request, 'Your new password was saved!')
                return HttpResponseRedirect('/quest/user_login')

    return HttpResponseRedirect('/quest/user_forgot_password/' + ldap)

def go_back_to_login(request, ldap):
    if request.method == 'POST':
        current_user = User.objects.get(user_ldap = ldap)
        current_user.user_reset_password_pin = None
        current_user.save()
    return HttpResponseRedirect('/quest/user_login')


####################################

def get_user_settings_info(request, ldap):
    
    if not validate_user_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    current_user = User.objects.get(user_ldap = ldap)
    context = {'current_user': current_user}
    return render(request, 'quest_extension/user_settings_info.html', context)

def update_user_ldap(request, ldap):
    
    if not validate_user_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    current_user = User.objects.get(user_ldap = ldap)
    if request.method == 'POST':
        post_request = request.POST
        ldap_input = post_request['user_ldap']
        is_new_ldap = ldap_input not in User.objects.all().values_list('user_ldap', flat=True) 
        if (is_new_ldap):
            current_user.user_ldap = ldap_input
            current_user.save()
            request.session['current_user_ldap'] = ldap_input
            messages.success(request, 'Change was successful!')

        else:
             messages.error(request, 'There is already an account associated with this LDAP')
    return HttpResponseRedirect('/quest/user_settings_info/' + current_user.user_ldap)

def update_user_first_name(request, ldap):
    if not validate_user_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    current_user = User.objects.get(user_ldap = ldap)
    if request.method == 'POST':
        post_request = request.POST
        first_name_input = post_request['user_first_name']
        current_user.user_first_name = first_name_input
        current_user.save()
        messages.success(request, 'Change was successful!')


    return HttpResponseRedirect('/quest/user_settings_info/' + current_user.user_ldap)

def update_user_last_name(request, ldap):
    if not validate_user_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    current_user = User.objects.get(user_ldap = ldap)
    if request.method == 'POST':
        post_request = request.POST
        last_name_input = post_request['user_last_name']
        current_user.user_last_name = last_name_input
        current_user.save()
        messages.success(request, 'Change was successful!')

    return HttpResponseRedirect('/quest/user_settings_info/' + current_user.user_ldap)

def update_user_email(request, ldap):
    if not validate_user_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    current_user = User.objects.get(user_ldap = ldap)
    if request.method == 'POST':
        post_request = request.POST
        user_email_input = post_request['user_email']
        try:
            validate_email(user_email_input)
            current_user.user_email = user_email_input
            current_user.save()
            messages.success(request, 'Change was successful!')
        except:
            messages.error(request, 'This is an invalid email')
    return HttpResponseRedirect('/quest/user_settings_info/' + current_user.user_ldap)


def update_user_password(request, ldap):
    if not validate_user_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    current_user = User.objects.get(user_ldap = ldap)
    if request.method == 'POST':
        post_request = request.POST
        user_current_password = make_hash(post_request['current_password'])
        user_new_password = make_hash(post_request['new_password'])
        user_new_password_retyped = make_hash(post_request['retyped_password'])
        if user_current_password != current_user.user_password:
            messages.error(request, 'Your current password was typed incorrectly')
        elif user_new_password != user_new_password_retyped:
            messages.error(request, 'Your new passwords do not match')
        else:
            current_user.user_password = user_new_password
            current_user.save()
            messages.success(request, 'Change was successful!')

    return HttpResponseRedirect('/quest/user_settings_info/' + current_user.user_ldap)


    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #################################################################################
    #All admin views

def get_admin_login(request):

    if 'current_admin_ldap' in request.session:
        del request.session['current_admin_ldap']

    #This session will only last while a user is in either an editable or non-editable path
    #We use this session to differentiate between viewable or editable paths
    if 'view_or_editable' in request.session:
        del request.session['view_or_editable']

    login_form = LoginForm()
    context = {'login_form': login_form}
    return render(request, 'quest_extension/admin_login.html', context)

def admin_login_to_account(request):
    if request.method == 'POST':
        post_request = request.POST
        ldap = post_request['ldap']
        password = make_hash(post_request['password'])
        print (post_request)

        if Admin.objects.filter(admin_ldap = ldap):
            #If incorrect password
            if not Admin.objects.get(admin_ldap = ldap).admin_password == password:
                messages.error(request, 'Invalid Password')
            #If correct password for ldap
            else: 
                request.session['current_admin_ldap'] = post_request['ldap']
                return HttpResponseRedirect('/quest/admin_project_page/' + request.session['current_admin_ldap'])
        #If LDAP is not associated with an account
        else:
            messages.error(request, 'There is no admin account associated with this LDAP')
    
    return HttpResponseRedirect('/quest/admin_login')

def admin_change_password_request(request):
    if request.method == 'POST':
        post_request = request.POST
        ldap = post_request['ldap']

        #only proceed if there is an Admin with this ldap
        if not Admin.objects.filter(admin_ldap = ldap):
            messages.error(request, 'There is no admin account with this ldap')
            return HttpResponseRedirect('/quest/admin_login')

        else:
            current_admin = Admin.objects.get(admin_ldap = ldap)
            pin = str(random.randint(99999, 999999))
            current_admin.admin_reset_password_pin = pin
            current_admin.save()
            message_body = ('Hi ' + current_admin.admin_first_name + '. We have just recieved notice that you requested ' +
            'to create a new password! Your six digit pin is ' + str(pin))
            send_mail(
            'Password Reset',
            message_body,
            'icet.tushar@gmail.com', #This will have to change once we deploy this on a remote server
            [current_admin.admin_email],
            fail_silently=False,
            )
            print('MAIL SENT')
            return HttpResponseRedirect('/quest/admin_forgot_password/' + ldap)
    
        return HttpResponseRedirect('/quest/admin_login')


####################################

def get_new_admin_page(request):

    admin_form = AdminForm()
    context = {'admin_form': admin_form}
    return render(request, 'quest_extension/new_admin.html', context)

def add_new_admin(request):
    if request.method == 'POST':
        post_request = request.POST
        retyped_password = make_hash(post_request['retyped_password'])
        admin_form = AdminForm(request.POST)
        if admin_form.is_valid():
            temp = admin_form.save(commit=False)
            email = temp.admin_email
            admin_ldap = temp.admin_ldap
            admin_password = temp.admin_password
            admin_password = make_hash(admin_password)
            temp.admin_password = admin_password
            try:
                validate_email(email)
                valid_email = True
            except:
                valid_email = False
                print("This is an invalid email")
                messages.error(request, 'Please input a valid email')
                return HttpResponseRedirect('/quest/new_admin') 

            valid_password = (retyped_password == temp.admin_password)
            is_new_ldap = admin_ldap not in Admin.objects.all().values_list('admin_ldap', flat=True) 
            if valid_email and is_new_ldap and valid_password:
                temp.save()
                messages.success(request, 'Your new account was created!')
                return HttpResponseRedirect('/quest/admin_login')
            if not is_new_ldap:
                messages.error(request, 'There is already an account associated with this LDAP')
            if not valid_password:
                messages.error(request, 'Your Password and Retyped Password do not match')

    return HttpResponseRedirect('/quest/new_admin')

####################################

def get_admin_forgot_password(request, ldap):
    forgot_password_form = ForgotPasswordForm()
    context = {'forgot_password_form': forgot_password_form, 'ldap': ldap}
    return render(request, 'quest_extension/admin_forgot_password.html', context)


def admin_new_password_sent(request, ldap):
    current_admin = Admin.objects.get(admin_ldap = ldap)
    if request.method == 'POST':
        forgot_password_form = ForgotPasswordForm(request.POST)
        if forgot_password_form.is_valid():
            pin = forgot_password_form.cleaned_data['pin']
            new_password = make_hash(forgot_password_form.cleaned_data['new_password'])
            retype_new_password = make_hash(forgot_password_form.cleaned_data['retype_new_password'])

            if (current_admin.admin_reset_password_pin != pin):
                messages.error(request,'Pin does not match the sent pin')
                return HttpResponseRedirect ('/quest/admin_forgot_password/' + ldap)
            elif (new_password != retype_new_password):
                messages.error(request, 'Your Passwords do not match')
                return HttpResponseRedirect ('/quest/admin_forgot_password/' + ldap)
            else:
                current_admin.admin_password = new_password
                #By setting this value to none as soon as possible, it leaves a very small window for
                #an intruder to try guessing the admins pin
                current_admin.admin_reset_password_pin = None
                current_admin.save()
                messages.success(request, 'Your new password was saved!')
                return HttpResponseRedirect('/quest/admin_login')

    return HttpResponseRedirect('/quest/admin_forgot_password/' + ldap)


def admin_go_back_to_login(request, ldap):
    if request.method == 'POST':
        current_admin = Admin.objects.get(admin_ldap = ldap)
        current_admin.admin_reset_password_pin = None
        current_admin.save()
    return HttpResponseRedirect('/quest/admin_login')



#########################


def get_admin_project_settings_editable(request, ldap, project_id):

    if not (validate_admin_access(request, ldap) and can_admin_access_project(ldap, project_id)):
        return HttpResponseRedirect('/quest/admin_login')

    current_project = Project.objects.get(id = project_id)


    if not is_still_editable(current_project):
        messages.warning(request, 'Someone has joined the project, so you must re-enter it in the view only mode')
        return HttpResponseRedirect('/quest/admin_project_page/' + ldap)

    view_or_editable = request.session['view_or_editable']

    current_admin = Admin.objects.get(admin_ldap = ldap)

    #Represents all admins for this project
    list_of_admins = AdminProject.objects.filter(project = current_project).values_list('admin', flat = True)
    list_of_admins = Admin.objects.filter(pk__in=list_of_admins)
    has_teams = current_project.project_has_teams
    list_of_teams = Team.objects.filter(project = current_project)


    context = {
    'current_project': current_project, 
    'current_admin': current_admin, 
    'list_of_admins': list_of_admins, 
    'view_or_editable': view_or_editable,
    'has_teams': has_teams,
    'list_of_teams': list_of_teams,
    }
    return render(request, 'quest_extension/admin_project_settings_editable.html', context)


def update_random_phrase(request, ldap, project_id):

    if not (validate_admin_access(request, ldap) and can_admin_access_project(ldap, project_id)):
        return HttpResponseRedirect('/quest/admin_login')

    current_project = Project.objects.get(id = project_id)
    if request.method == 'POST':
        post_request = request.POST
        random_phrase_input = post_request['project_random_phrase']
        is_new_random_phrase = random_phrase_input not in Project.objects.all().values_list('project_random_phrase', flat=True) 
        if (is_new_random_phrase):
            current_project.project_random_phrase = random_phrase_input
            current_project.save()
            messages.success(request, 'Random phrase updated successfully!')

        else:
             messages.error(request, 'You must choose a different random phrase')
    
    return redirect_to_correct_project_settings_page(request.session['view_or_editable'], ldap, project_id)

    

def update_admin_pin(request, ldap, project_id):
    if not (validate_admin_access(request, ldap) and can_admin_access_project(ldap, project_id)):
        return HttpResponseRedirect('/quest/admin_login')

    current_project = Project.objects.get(id = project_id)
    if request.method == 'POST':
        post_request = request.POST
        admin_pin_input = post_request['project_admin_pin']
        is_new_admin_pin = admin_pin_input not in Project.objects.all().values_list('project_admin_pin', flat=True) 
        if (is_new_admin_pin):
            current_project.project_admin_pin = admin_pin_input
            current_project.save()
            messages.success(request, 'Admin pin updated successfully!')

        else:
             messages.error(request, 'You must choose a different admin pin')
    
    return redirect_to_correct_project_settings_page(request.session['view_or_editable'], ldap, project_id)


def remove_as_admin(request, ldap, project_id):
    if not (validate_admin_access(request, ldap) and can_admin_access_project(ldap, project_id)):
        return HttpResponseRedirect('/quest/admin_login')

    current_project = Project.objects.get(id = project_id)
    current_admin = Admin.objects.get(admin_ldap = ldap)
    AdminProject.objects.get(project = current_project, admin = current_admin).delete()
    messages.success(request, 'You are no longer an admin of ' + current_project.project_name + '!')
    
    return HttpResponseRedirect('/quest/admin_project_page/' + ldap)

    
#Should only be available in the view_only mode, since there's no use in editable
def remove_all_users(request, ldap, project_id):
    
    if not (validate_admin_access(request, ldap) and can_admin_access_project(ldap, project_id)):
            return HttpResponseRedirect('/quest/admin_login')

    current_project = Project.objects.get(id = project_id)
    current_project.project_editable = True
    current_project.save()
    delete_all_user_projects = UserProject.objects.filter(project = current_project).delete()
    messages.success(request, 'All users from "' + current_project.project_name + '" were removed, and the project is now editable!')
    return HttpResponseRedirect('/quest/admin_project_page/' + ldap)


def delete_project(request, ldap, project_id):
    if not (validate_admin_access(request, ldap) and can_admin_access_project(ldap, project_id)):
        return HttpResponseRedirect('/quest/admin_login')

    if request.method == 'POST':
        current_project = Project.objects.get(id = project_id)
        current_project.delete()
        messages.success(request, 'You have successfully deleted the project "' + current_project.project_name + '"')

    
    return HttpResponseRedirect('/quest/admin_project_page/' + ldap)

#Only allowable in editable mode
def add_team(request, ldap, project_id):

    if not (validate_admin_access(request, ldap) and can_admin_access_project(ldap, project_id)):
        return HttpResponseRedirect('/quest/admin_login')

    current_project = Project.objects.get(id = project_id)

    if not is_still_editable(current_project):
        messages.warning(request, 'Someone has joined the project, so you must re-enter it in the view only mode')
        return HttpResponseRedirect('/quest/admin_project_page/' + ldap)

    
    list_of_team_names = Team.objects.filter(project = current_project).values_list('team_name', flat=True)
    if request.method == 'POST':
        post_request = request.POST
        team_name_to_add = post_request['add_team_name'].strip()
        if team_name_to_add in list_of_team_names:
            messages.error(request, 'You cannot have two teams with the same name')
        else:
            if not current_project.project_has_teams:
                current_project.project_has_teams = True
                current_project.save()
            new_team = Team()
            new_team.team_name = team_name_to_add
            new_team.project = current_project
            new_team.save()
    messages.success(request, 'New team successfully added!')
    return redirect_to_correct_project_settings_page(request.session['view_or_editable'], ldap, project_id)
    
def delete_team(request, ldap, project_id):

    if not (validate_admin_access(request, ldap) and can_admin_access_project(ldap, project_id)):
        return HttpResponseRedirect('/quest/admin_login')
    
    current_project = Project.objects.get(id = project_id)
    list_of_team_names = Team.objects.filter(project = current_project).values_list('team_name', flat=True)

    if request.method == 'POST':
        post_request = request.POST
        team_name_to_delete = post_request['delete_team_name'].strip()
        if team_name_to_delete not in list_of_team_names:
            messages.error(request, 'There is no team with this name in this project')
        else:
            # If we are deleting the last team in this project
            if len(list_of_team_names) == 1:
                current_project.project_has_teams = False
                current_project.save()
            team_to_delete = Team.objects.get(project = current_project, team_name = team_name_to_delete)
            team_to_delete.delete()
    messages.success(request, 'Team successfully deleted!')
    return redirect_to_correct_project_settings_page(request.session['view_or_editable'], ldap, project_id)




#########################


def get_admin_project_settings_view_only(request, ldap, project_id):

    if not (validate_admin_access(request, ldap) and can_admin_access_project(ldap, project_id)):
        return HttpResponseRedirect('/quest/admin_login')

    view_or_editable = request.session['view_or_editable']

    current_admin = Admin.objects.get(admin_ldap = ldap)
    current_project = Project.objects.get(id = project_id)

    #Represents all admins for this project
    list_of_admins = AdminProject.objects.filter(project = current_project).values_list('admin', flat = True)
    list_of_admins = Admin.objects.filter(pk__in=list_of_admins)
    has_teams = current_project.project_has_teams
    list_of_teams = Team.objects.filter(project = current_project)


    context = {
    'current_project': current_project, 
    'current_admin': current_admin, 
    'list_of_admins': list_of_admins, 
    'view_or_editable': view_or_editable,
    'has_teams': has_teams,
    'list_of_teams': list_of_teams,
    }
    return render(request, 'quest_extension/admin_project_settings_view_only.html', context)




#########################

def get_admin_settings_info(request, ldap):
    
    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    current_admin = Admin.objects.get(admin_ldap = ldap)
    context = {'current_admin': current_admin}
    return render(request, 'quest_extension/admin_settings_info.html', context)

def update_admin_ldap(request, ldap):
    
    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    current_admin = Admin.objects.get(admin_ldap = ldap)
    if request.method == 'POST':
        post_request = request.POST
        ldap_input = post_request['admin_ldap']
        is_new_ldap = ldap_input not in Admin.objects.all().values_list('admin_ldap', flat=True) 
        if (is_new_ldap):
            current_admin.admin_ldap = ldap_input
            current_admin.save()
            request.session['current_admin_ldap'] = ldap_input
            messages.success(request, 'LDAP updated successfully!')

        else:
             messages.error(request, 'There is already an account associated with this LDAP')
    return HttpResponseRedirect('/quest/admin_settings_info/' + current_admin.admin_ldap)

def update_admin_first_name(request, ldap):

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    current_admin = Admin.objects.get(admin_ldap = ldap)
    if request.method == 'POST':
        post_request = request.POST
        first_name_input = post_request['admin_first_name']
        current_admin.admin_first_name = first_name_input
        current_admin.save()
        messages.success(request, 'First name updated successfully!')


    return HttpResponseRedirect('/quest/admin_settings_info/' + current_admin.admin_ldap)

def update_admin_last_name(request, ldap):
    
    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    current_admin = Admin.objects.get(admin_ldap = ldap)
    if request.method == 'POST':
        post_request = request.POST
        last_name_input = post_request['admin_last_name']
        current_admin.admin_last_name = last_name_input
        current_admin.save()
        messages.success(request, 'Last name updated successfully!')

    return HttpResponseRedirect('/quest/admin_settings_info/' + current_admin.admin_ldap)

def update_admin_email(request, ldap):
    
    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    current_admin = Admin.objects.get(admin_ldap = ldap)
    if request.method == 'POST':
        post_request = request.POST
        admin_email_input = post_request['admin_email']
        try:
            validate_email(admin_email_input)
            current_admin.admin_email = admin_email_input
            current_admin.save()
            messages.success(request, 'Email updated successfully!')
        except:
            messages.error(request, 'This is an invalid email')
    return HttpResponseRedirect('/quest/admin_settings_info/' + current_admin.admin_ldap)


def update_admin_password(request, ldap):
    
    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    current_admin = Admin.objects.get(admin_ldap = ldap)
    if request.method == 'POST':
        post_request = request.POST
        admin_current_password = make_hash(post_request['current_password'])
        admin_new_password = make_hash(post_request['new_password'])
        admin_new_password_retyped = make_hash(post_request['retyped_password'])
        if admin_current_password != current_admin.admin_password:
            messages.error(request, 'Your current password was typed incorrectly')
        elif admin_new_password != admin_new_password_retyped:
            messages.error(request, 'Your new passwords do not match')
        else:
            current_admin.admin_password = admin_new_password
            current_admin.save()
            messages.success(request, 'Password updated successfully!')

    return HttpResponseRedirect('/quest/admin_settings_info/' + current_admin.admin_ldap)


#########################

def get_admin_project_info_page(request, ldap, project_id):
    current_project = Project.objects.get(id = project_id)
    current_admin = Admin.objects.get(admin_ldap = ldap)
    view_or_editable = request.session['view_or_editable'] 


    if not (validate_admin_access(request, ldap) and can_admin_access_project(ldap, project_id)):
        return HttpResponseRedirect('/quest/admin_login')

    context = {'current_project': current_project, 'current_admin': current_admin, 'view_or_editable': view_or_editable}
    return render(request, 'quest_extension/admin_project_info_page.html', context)


def search_by_user_ldap(request, ldap, project_id):
    print('I AM HERE')
    current_project = Project.objects.get(id = project_id)
    current_admin = Admin.objects.get(admin_ldap = ldap)
    view_or_editable = request.session['view_or_editable'] 

    if not (validate_admin_access(request, ldap) and can_admin_access_project(ldap, project_id)):
        return HttpResponseRedirect('/quest/admin_login')

    if request.method == 'POST':
        post_request = request.POST
        user_requested_for = post_request['user']
        if User.objects.filter(user_ldap = user_requested_for):
            user_requested_for = User.objects.get(user_ldap = user_requested_for)
        else:
            messages.warning(request, 'User with ldap "' + post_request['user'] + '" does not exist')
            return HttpResponseRedirect('/quest/admin_project_info_page/' + ldap + '/' + project_id)

        if UserProject.objects.filter(user = user_requested_for, project = current_project):
            user_project_info = UserProject.objects.filter(user = user_requested_for, project = current_project)
            messages.success(request, 'User information found!')

        else:
            messages.warning(request, 'User with ldap "' + post_request['user'] + '" is not a part of this project')
            return HttpResponseRedirect('/quest/admin_project_info_page/' + ldap + '/' + project_id)
    
    query = 'LDAP = ' + post_request['user']
    context = {
    'current_project': current_project, 
    'current_admin': current_admin, 
    'user_project_info': user_project_info, 
    'query': query,
    'view_or_editable': view_or_editable
    }
    return render(request, 'quest_extension/admin_project_info_page.html', context)


def search_above(request, ldap, project_id):
    current_project = Project.objects.get(id = project_id)
    current_admin = Admin.objects.get(admin_ldap = ldap)
    view_or_editable = request.session['view_or_editable'] 


    if not (validate_admin_access(request, ldap) and can_admin_access_project(ldap, project_id)):
        return HttpResponseRedirect('/quest/admin_login')

    highest_quest_path_number = max(Quest.objects.filter(project = current_project).values_list('quest_path_number', flat = True))
    if request.method == 'POST':
        post_request = request.POST
        above = post_request ['above']

        if Quest.objects.filter(project = current_project, quest_path_number__gt = above):
            valid_quests = Quest.objects.filter(project = current_project, quest_path_number__gt = int(above))
            messages.success(request, 'Users\' information found!')
        else:
            messages.warning(request, 'There are no quests that have a path greater than ' + above  
            + ' (the highest quest path number in this project is ' + str(highest_quest_path_number) + ')')
            return HttpResponseRedirect('/quest/admin_project_info_page/' + ldap + '/' + project_id)

        user_project_info = UserProject.objects.filter(current_quest__in = valid_quests, project = current_project)

    query = 'Quest Path Number > ' + str(above)
    context = {
    'current_project': current_project,
    'current_admin': current_admin, 
    'user_project_info': user_project_info, 
    'query': query,
    'view_or_editable': view_or_editable
    }
    return render(request, 'quest_extension/admin_project_info_page.html', context)


def search_below(request, ldap, project_id):
    current_project = Project.objects.get(id = project_id)
    current_admin = Admin.objects.get(admin_ldap = ldap)
    view_or_editable = request.session['view_or_editable'] 


    if not (validate_admin_access(request, ldap) and can_admin_access_project(ldap, project_id)):
        return HttpResponseRedirect('/quest/admin_login')

    lowest_quest_path_number = min(Quest.objects.filter(project = current_project).values_list('quest_path_number', flat = True))
    if request.method == 'POST':
        post_request = request.POST
        below = post_request ['below']

        if Quest.objects.filter(project = current_project, quest_path_number__lt = below):
            valid_quests = Quest.objects.filter(project = current_project, quest_path_number__lt = int(below))
            messages.success(request, 'Users\' information found!')
        else:
            messages.warning(request, 'There are no quests that have a path lower than ' + below  
            + ' (the lowest quest path number in this project is ' + str(lowest_quest_path_number) + ')')
            return HttpResponseRedirect('/quest/admin_project_info_page/' + ldap + '/' + project_id)

        user_project_info = UserProject.objects.filter(current_quest__in = valid_quests, project = current_project)

    query = 'Quest Path Number > ' + str(below)
    context = {
        'current_project': current_project, 
        'current_admin': current_admin, 
        'user_project_info': user_project_info, 
        'query': query,
        'view_or_editable': view_or_editable
        }
    return render(request, 'quest_extension/admin_project_info_page.html', context)



def search_at(request, ldap, project_id):
    current_project = Project.objects.get(id = project_id)
    current_admin = Admin.objects.get(admin_ldap = ldap)
    view_or_editable = request.session['view_or_editable'] 

    if not (validate_admin_access(request, ldap) and can_admin_access_project(ldap, project_id)):
        return HttpResponseRedirect('/quest/admin_login')

    if request.method == 'POST':
        post_request = request.POST
        at = post_request ['at']

        if Quest.objects.filter(project = current_project, quest_path_number = at):
            valid_quests = Quest.objects.filter(project = current_project, quest_path_number = at)
            messages.success(request, 'Users\' information found!')
        else:
            messages.warning(request, 'There are no quests with the path number ' + str(at))
            return HttpResponseRedirect('/quest/admin_project_info_page/' + ldap + '/' + project_id)

        user_project_info = UserProject.objects.filter(current_quest__in = valid_quests, project = current_project)

    query = 'Quest Path Number = ' + str(at)
    context = {
    'current_project': current_project, 
    'current_admin': current_admin, 
    'user_project_info': user_project_info, 
    'query': query,
    'view_or_editable': view_or_editable,
    }
    return render(request, 'quest_extension/admin_project_info_page.html', context)


def search_all_users(request, ldap, project_id):

    current_project = Project.objects.get(id = project_id)
    current_admin = Admin.objects.get(admin_ldap = ldap)
    view_or_editable = request.session['view_or_editable'] 

    if not (validate_admin_access(request, ldap) and can_admin_access_project(ldap, project_id)):
        return HttpResponseRedirect('/quest/admin_login')

    if request.method == 'POST':
        post_request = request.POST

        user_project_info = UserProject.objects.filter(project = current_project)
        messages.success(request, 'Users\' information found')

    query = 'All Users'
    context = {
    'current_project': current_project, 
    'current_admin': current_admin, 
    'user_project_info': user_project_info, 
    'query': query,
    'view_or_editable': view_or_editable
    }
    return render(request, 'quest_extension/admin_project_info_page.html', context)



def search_completed_users(request, ldap, project_id):
    current_project = Project.objects.get(id = project_id)
    current_admin = Admin.objects.get(admin_ldap = ldap)
    view_or_editable = request.session['view_or_editable'] 


    if not (validate_admin_access(request, ldap) and can_admin_access_project(ldap, project_id)):
        return HttpResponseRedirect('/quest/admin_login')

    if request.method == 'POST':
        post_request = request.POST

        user_project_info = UserProject.objects.filter(project = current_project, completed_project = True)
        messages.success(request, 'Users\' information found')


    query = 'All Users that completed the project'
    context = {
        'current_project': current_project, 
        'current_admin': current_admin, 
        'user_project_info': user_project_info, 
        'query': query,
        'view_or_editable': view_or_editable
        }
    return render(request, 'quest_extension/admin_project_info_page.html', context)



def search_not_completed_users(request, ldap, project_id):
    current_project = Project.objects.get(id = project_id)
    current_admin = Admin.objects.get(admin_ldap = ldap)
    view_or_editable = request.session['view_or_editable'] 


    if not (validate_admin_access(request, ldap) and can_admin_access_project(ldap, project_id)):
        return HttpResponseRedirect('/quest/admin_login')

    if request.method == 'POST':
        post_request = request.POST

        user_project_info = UserProject.objects.filter(project = current_project, completed_project = False)
        messages.success(request, 'Users\' information found')


    query = 'All Users that have not completed the project'
    context = {
    'current_project': current_project, 
    'current_admin': current_admin, 
    'user_project_info': user_project_info, 
    'query': query,
    'view_or_editable': view_or_editable
    }
    return render(request, 'quest_extension/admin_project_info_page.html', context)











    

    
 


