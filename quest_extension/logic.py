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
from django.db.models import Sum
import hashlib
import requests




#Saves a free response question to the backend
def save_fr_question(request, ldap, question_form, answer_form, quest_id, timestamp=datetime.now()):
    quest = Quest.objects.get(id=quest_id)
    q_form = question_form.save(commit=False)
    q_form.question_type = 'FR'
    
    q_form.quest = quest
    q_form.save()
    question_id = q_form.id
    Question.objects.filter(id = question_id).update(time_modified = timestamp)
    current_question = Question.objects.get(id = question_id)
    print(current_question.time_modified)

    a_form = answer_form.save(commit=False)
    a_form.question = Question.objects.get(id=question_id)
    a_form.save()
    return HttpResponseRedirect('/quest/admin_quest_page_editable/' + ldap + '/' + str(quest_id))


#Saves a multiple choice question to the backend
def save_mc_question(request, ldap, question_form, answer_form, wrong_answer_form, quest_id, timestamp=datetime.now()):

    quest_id = str(quest_id)
    quest = Quest.objects.get(id=quest_id)
    q_form = question_form.save(commit=False)
    q_form.question_type = 'MC'
    q_form.quest = quest
    q_form.save()
    question_id = q_form.id
    #This allows us to bypass the automatic date from auto_now
    Question.objects.filter(id = question_id).update(time_modified = timestamp)
    
    current_question = Question.objects.get(id = question_id)
    print(current_question.time_modified)
    

    list_of_correct_answers = answer_form.cleaned_data['correct_choices'].split('\n')
    #Removes blank correct answers
    list_of_correct_answers = [x for x in list_of_correct_answers if len(x.strip())>0]


    for correct_answer in list_of_correct_answers:
        correct_answer = str(correct_answer).strip()
        a_form = CorrectAnswer(question=Question.objects.get(id=question_id), answer_text= correct_answer)
        a_form.save()

    list_of_wrong_answers = wrong_answer_form.cleaned_data['incorrect_choices'].split('\n')
    #Removes blank wrong answers
    list_of_wrong_answers = [x for x in list_of_wrong_answers if len(x.strip())>0]


    for wrong_answer in list_of_wrong_answers:
        wrong_answer = str(wrong_answer).strip()
        w_a_form = IncorrectAnswer(question=Question.objects.get(id=question_id), answer_text= wrong_answer)
        w_a_form.save()
    
    messages.success(request, 'New question successfully created!')
    return HttpResponseRedirect('/quest/admin_quest_page_editable/' + ldap + '/' + quest_id)

# Saves an API Question
def save_api_question(request, ldap, question_form, quest_id, timestamp=datetime.now()):
    api_url = request.POST['api_url']
    current_quest = Quest.objects.get(id = quest_id)
    
    q_form = question_form.save(commit=False)
    q_form.question_type = 'API'
    q_form.question_api_url = api_url
    q_form.quest = current_quest
    q_form.save()
    question_id = q_form.id
    Question.objects.filter(id = question_id).update(time_modified = timestamp)
    return HttpResponseRedirect('/quest/admin_quest_page_editable/' + ldap + '/' + str(quest_id))

# Verifies whether the given API URL returns true or false and can take in an ldap query parameter
def is_api_url_valid(request, api_url, ldap, quest_id):
    php_result = 'invalid'

    # I am passing an example queryparameter -> the api code should return false for something like this
    payload = {'ldap': 'example'}
    try:
        php_result = str(requests.get(api_url, params = payload).content)
    except:
        return False


    if 'true' not in php_result and 'false' not in php_result:
        return False
    
    return True



#Verifies that you are only trying to access the content for the ldap that you are logged in for
def validate_user_access(request, ldap):
    return 'current_user_ldap' in request.session and request.session['current_user_ldap'] == ldap 

#By having a separate one for admin access instead of using an "or" and one method is that now you MUST
#have an admin session running to be able to go into Admin Pages
def validate_admin_access(request, ldap):
    return 'current_admin_ldap' in request.session and request.session['current_admin_ldap'] == ldap
        
    

#Checks whether you can go to the next question once you sumbit a new answer
def go_to_next_quest(current_quest, current_user, current_project):
    num_questions_in_quest = len(Question.objects.filter(quest = current_quest, deleted = False))
    # all_questions_in_quest = [question for question in Question.objects.filter(quest = current_quest, deleted = False)]
    current_user_project = UserProject.objects.get(user = current_user, project = current_project)
    # count_of_correctly_answered_questions = 0
    # for question in all_questions_in_quest:
    #     if (CorrectlyAnsweredQuestion.objects.filter(question = question, userproject = current_user_project)):
    #         count_of_correctly_answered_questions += 1
            
    all_question_ids_in_quest = Question.objects.filter(quest = current_quest).values_list('id', flat = True)
    count_of_correctly_answered_questions = len(CorrectlyAnsweredQuestion.objects.filter(userproject = current_user_project, question__in = all_question_ids_in_quest))
    print (CorrectlyAnsweredQuestion.objects.filter(userproject = current_user_project, question__in = all_question_ids_in_quest))

    print(count_of_correctly_answered_questions, num_questions_in_quest)
    if (count_of_correctly_answered_questions == num_questions_in_quest):
        users_user_project_object = UserProject.objects.get(user = current_user, project = current_project)
        #adds points for the completed quest to the user
        users_user_project_object.points += current_quest.quest_points_earned
        users_user_project_object.save()
        print("Edli's points are:" + str (users_user_project_object.points))
        current_quest_num = current_quest.quest_path_number
        #If next quest exists
        if (Quest.objects.filter(quest_path_number = current_quest_num + 1, project = current_project)):
            next_quest = Quest.objects.get(quest_path_number = current_quest_num + 1, project = current_project)
            print("I Am Here")
            users_user_project_object.current_quest = next_quest
            users_user_project_object.save()
        else:
            print('I am actually here')
            users_user_project_object.completed_project = True
            users_user_project_object.save()

#Checks whether an Admin can access a Quest
def can_admin_access_quest(ldap, quest_id):

    if not Quest.objects.filter(id = quest_id):
        return False

    current_quest = Quest.objects.get(id = quest_id)
    project_id = current_quest.project.id

    return can_admin_access_project(ldap, project_id)

            

#Checks whether an Admin can access a Project
def can_admin_access_project(ldap, project_id):

    if not (Admin.objects.filter(admin_ldap = ldap) and Project.objects.filter(id = project_id)):
        return False

    current_admin = Admin.objects.get(admin_ldap = ldap)
    current_project = Project.objects.get(id = project_id)

    list_of_projects = AdminProject.objects.filter(admin = current_admin).values('project')
    list_of_projects = Project.objects.filter(pk__in=list_of_projects)
    return current_project in list_of_projects
    
#Gets the team and points format that is used in the admin and user home pages
def get_team_points_format(current_project):
    all_teams_and_points = {}
    all_teams_in_project = Team.objects.filter(project = current_project)
    for team in all_teams_in_project:
        current_points_for_team = UserProject.objects.filter(team = team).aggregate(points = Sum('points'))
        current_points_for_team = current_points_for_team['points']
        if current_points_for_team == None:
            current_points_for_team = 0

        all_points_in_project = Quest.objects.filter(project = current_project).aggregate(total_points_in_quest = Sum('quest_points_earned'))
        all_points_in_project = all_points_in_project['total_points_in_quest']
        
        # For development purposes (this will never happen if someone joins a completed project)
        if all_points_in_project == None:
            all_points_in_project = 0

        users_on_this_team = UserProject.objects.filter(team = team).count()
        print(all_points_in_project, users_on_this_team)
        total_possible_points_for_team = all_points_in_project * users_on_this_team
        
        #format = teamname -> (current points earned by team, total points that can be earned by team)
        all_teams_and_points[team.team_name] = (current_points_for_team, total_possible_points_for_team)
    return all_teams_and_points

#if an admin is inside of a project and changing aspects of it, we want to stop this as 
#soon as someone joins the proejct
def is_still_editable(current_project):
    print (len(UserProject.objects.filter(project = current_project)))
    return len(UserProject.objects.filter(project = current_project)) == 0

def redirect_to_correct_home_page(view_or_editable, ldap, project_id):
    if view_or_editable == 'editable':
        return HttpResponseRedirect('/quest/admin_home_editable/' + ldap + '/' + str(project_id))

    else:
        return HttpResponseRedirect('/quest/admin_home_view_only/' + ldap + '/' + str(project_id)) 

def redirect_to_correct_quest_page(view_or_editable, ldap, quest_id):
    if view_or_editable == 'editable':  
        return HttpResponseRedirect('/quest/admin_quest_page_editable/' + ldap + '/' + str(quest_id))
    else:
        return HttpResponseRedirect('/quest/admin_quest_page_view_only/' + ldap + '/' + str(quest_id))

def redirect_to_correct_project_settings_page(view_or_editable, ldap, project_id):
    if view_or_editable == 'view':
        return HttpResponseRedirect('/quest/admin_project_settings_view_only/' + ldap + '/' + project_id)
    else:
        return HttpResponseRedirect('/quest/admin_project_settings_editable/' + ldap + '/' + project_id)


def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hash(password, hash):
    if make_hash(password) == hash:
        return True
    return False


#Validates whether an api question is correctly answered
def validate_api_question_response(request, ldap, question):
    current_user = User.objects.get(user_ldap = ldap)
    current_question = question
    current_quest = question.quest
    current_project = current_quest.project
    current_user_project = UserProject.objects.get(user = current_user, project = current_project)

    question_url = question.question_api_url

    payload = {'ldap': ldap}


    php_result = str(requests.get(question_url, params = payload).content)

    if 'true' in php_result:
        correctly_answered_question = CorrectlyAnsweredQuestion()
        #Adds a new correctly answer question
        correctly_answered_question.question = current_question
        correctly_answered_question.userproject = current_user_project
        correctly_answered_question.save()        
        go_to_next_quest(current_quest, current_user, current_project)
        messages.success(request, 'That\'s correct!!' , extra_tags = str(current_question.id))
    elif 'false' in php_result:
        messages.error(request, 'Sorry, you have not completed this task yet :(', extra_tags = str(current_question.id))





#Validates whether a mc or fr question is correctly answered
def validate_mc_or_fr_question_response(request, ldap, question, user_answer):
   
    current_quest = question.quest
    current_project = current_quest.project
    current_user = User.objects.get(user_ldap = ldap)
    current_user_project = UserProject.objects.get(user = current_user, project = current_project)
    current_question = question
    correct_answers = CorrectAnswer.objects.filter(question = current_question)

    correct_answers_texts = []
    for answer in correct_answers:
        correct_answers_texts.append(answer.answer_text)

    user_answer.sort()
    correct_answers_texts.sort()


    #Even if we need to select multiple answers to get the correct response, this will now work
    if user_answer == correct_answers_texts:
    #Creates a new MODEL INSTANCE of CorrectlyAnswerQuestions
        correctly_answered_question = CorrectlyAnsweredQuestion()
        #Adds a new correctly answer question
        correctly_answered_question.question = current_question
        correctly_answered_question.userproject = current_user_project
        correctly_answered_question.save()
        go_to_next_quest(current_quest, current_user, current_project)
        messages.success(request, 'That\'s correct!!' , extra_tags = str(current_question.id))
    else:
        messages.error(request, 'Sorry, that\'s not the right answer :(', extra_tags = str(current_question.id))


def create_admin_quest_page_format(list_of_questions):
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
    return format
    

