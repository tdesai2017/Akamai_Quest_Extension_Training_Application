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
from .logic import *
from django.core.mail import send_mail
import random



#Views

#For the creation of a FR question (not editing)
def get_fr_question_form(request, ldap, quest_id):

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    current_admin = Admin.objects.get(admin_ldap = ldap)
    question_form = QuestionForm()
    answer_form = CorrectAnswerForm()
    context = {'q_form' : question_form, 'ans_form' : answer_form, 'quest_id': quest_id, 'current_admin': current_admin}
    return render(request, 'quest_extension/fr_question_form.html', context)

def create_fr_question(request, ldap, quest_id):

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    if request.method  == 'POST':
        question_form = QuestionForm(request.POST)
        answer_form = CorrectAnswerForm(request.POST)
        if question_form.is_valid() and answer_form.is_valid():
            return save_fr_question(ldap, question_form, answer_form, quest_id)
    
    return HttpResponseRedirect('/quest/fr-create-form/' + ldap + '/' + str(quest_id))
    
    
######################################

#For the creation of a free response form (not editing)
def get_mc_question_form(request, ldap, quest_id):

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    current_admin = Admin.objects.get(admin_ldap = ldap)
    question_form = QuestionForm()
    answer_form = RightAnswerForm()
    wrong_answer_form = WrongAnswerForm()
    context = {'q_form' : question_form, 'ans_form' : answer_form, 'wrong_answer_form' : wrong_answer_form, 'quest_id': quest_id, 'current_admin': current_admin}
    return render(request, 'quest_extension/mc_question_form.html', context)


def create_mc_question(request, ldap, quest_id):

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    if request.method  == 'POST':
        question_form = QuestionForm(request.POST)
        answer_form = RightAnswerForm(request.POST)
        wrong_answer_form = WrongAnswerForm(request.POST)
        if question_form.is_valid() and answer_form.is_valid() and wrong_answer_form.is_valid():
            return save_mc_question(ldap, question_form, answer_form, wrong_answer_form, quest_id)
        
    return HttpResponseRedirect('/quest/mc-create-form/' + ldap + '/' + str(quest_id))


######################################


def get_admin_home_editable(request, ldap, project_id): 

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    current_admin = Admin.objects.get(admin_ldap = ldap)
    current_project = Project.objects.get(id = project_id)
    quests = Quest.objects.filter(project = current_project).order_by('quest_path_number')
    quest_form = QuestForm()
    context = {'quests':quests, 'quest_form': quest_form, 'current_project': current_project, 'current_admin': current_admin}
    return render(request, 'quest_extension/admin_home_editable.html', context)

def save_new_quest(request, ldap, project_id): 

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    current_project = Project.objects.get(id = project_id)
    if request.method == 'POST':
        post_request = request.POST
        quest_form = QuestForm(post_request)
        #Two quests cannot have the same path and paths must be greater than 0
        all_quests_in_current_project = Quest.objects.filter(project = current_project)
        all_paths_in_current_project = [quest.quest_path_number for quest in all_quests_in_current_project]
        if 'new_quest' in post_request and int(post_request['quest_path_number']) > 0 and int(post_request['quest_path_number']) not in all_paths_in_current_project:
            if quest_form.is_valid():
                temp = quest_form.save(commit=False)
                temp.project = current_project
                temp.save()
                quest_id = temp.id

                # If a user has no current quest for a certain project since the admin never created a quest with path 1 until
                # now, the user's current quest will be updated here to the inputted quest with id = 1
                all_users_without_current_quests = UserProject.objects.filter(project = current_project, current_quest= None)
                if int(post_request['quest_path_number']) == 1 and len(all_users_without_current_quests) > 0:
                    print('Yes we made it here at least', len(all_users_without_current_quests))
                    for userproject in all_users_without_current_quests:
                        userproject.current_quest = temp
                        userproject.save()

                return HttpResponseRedirect('/quest/admin_quest_page_editable/' + ldap + '/' + str(quest_id))

    return HttpResponseRedirect('/quest/admin_home_editable/' + ldap + '/' + str(project_id))

######################################


def get_admin_home_view_only(request, ldap,  project_id): 

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    current_admin = Admin.objects.get(admin_ldap = ldap)
    current_project = Project.objects.get(id = project_id)
    quests = Quest.objects.filter(project = current_project).order_by('quest_path_number')
    context = {'quests':quests, 'current_project': current_project, 'current_admin': current_admin}
    return render(request, 'quest_extension/admin_home_view_only.html', context)

######################################

def get_admin_quest_page_editable(request, ldap, quest_id):

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

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

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    if request.method == 'POST':
        post_request = request.POST
        current_question = Question.objects.get(id = post_request['deleted'])
        print (post_request)
        #We want to not let the time_modified increase, so we save it here and assign it to the question after we save it
        current_time_modified = copy.deepcopy(current_question.time_modified)
        current_question.deleted = True
        current_question.save()
        Question.objects.filter(id = post_request['deleted']).update(time_modified = current_time_modified)

    return HttpResponseRedirect('/quest/admin_quest_page_editable/' + ldap + '/' + str(quest_id))

def undo_delete_question(request, ldap, quest_id):

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    current_quest = Quest.objects.get(id = quest_id)
    if request.method == 'POST':        
        if Question.objects.filter(quest = current_quest, deleted = True):
            object_to_reappear = Question.objects.filter(quest = current_quest, deleted = True).latest('time_modified')
            #We want to not let the time_modified increase, so we save it here and assign it to the question after we save it
            object_to_reappear_id = object_to_reappear.id
            current_time_modified = copy.deepcopy(object_to_reappear.time_modified)
            object_to_reappear.deleted = False
            object_to_reappear.save()
            Question.objects.filter(id = object_to_reappear_id).update(time_modified = current_time_modified)

    return HttpResponseRedirect('/quest/admin_quest_page_editable/' + ldap + '/' + str(quest_id))


def save_video(request, ldap, quest_id):

    if not validate_admin_access(request, ldap):
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
            
    return HttpResponseRedirect('/quest/admin_quest_page_editable/' + ldap + '/' + str(quest_id))


def delete_video(request, ldap, quest_id):

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    if request.method == 'POST': 
        post_request = request.POST
        video_id = post_request['delete']
        video_to_delete = Video.objects.get(id = video_id)
        print("YOU ARE HERE", video_to_delete)
        video_to_delete.delete()
            
    return HttpResponseRedirect('/quest/admin_quest_page_editable/' + ldap + '/' + str(quest_id))



        



######################################

def get_admin_quest_page_view_only(request, ldap, quest_id):

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    current_admin = Admin.objects.get(admin_ldap = ldap)
    current_quest = Quest.objects.get(id = quest_id)
    current_project_id = current_quest.project.id
    list_of_questions = Question.objects.filter(quest = current_quest, deleted=False).order_by('time_modified')
    fr_input_form = TakeInFreeResponseForm()
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

    context = {'current_quest': current_quest, 'format': format, 'fr_input_form': fr_input_form, 'current_project_id': current_project_id, 'all_videos': all_videos, 'current_admin': current_admin}
    return render(request, 'quest_extension/admin_quest_page_view_only.html', context)

######################################

def get_user_home(request, ldap, project_id):

    if not validate_user_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    user = User.objects.get(user_ldap= ldap)
    current_project = Project.objects.get(id = project_id)
    current_user_project_object = UserProject.objects.get(user = user, project = current_project)
    quests = Quest.objects.filter(project = current_project).order_by('quest_path_number')
    context = {'quests':quests, 'user': user, 'current_project': current_project, 'current_user_project_object': current_user_project_object}
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
    have_correct_answer = [i.question.id for i in CorrectlyAnsweredQuestion.objects.filter(user = current_user)]


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

    context = {'current_quest': current_quest, 
            'fr_input_form': fr_input_form, 
            'ldap': ldap, 
            'current_project_id': current_project_id, 
            'have_correct_answer': have_correct_answer,
            'format_2': format_2,
            'all_videos': all_videos}

    return render(request, 'quest_extension/user_quest_page.html', context)

def validate_fr_question_response(request, ldap, quest_id):

    if not validate_user_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    current_quest = Quest.objects.get(id = quest_id)
    current_project = current_quest.project
    current_user = User.objects.get(user_ldap = ldap)

    if request.method == 'POST':
        #When do I check here whether the form is valid
        post_request = request.POST
        user_answer = post_request['answer']
        current_question = Question.objects.get(id = post_request['FR_response_id'])
        correct_answers = CorrectAnswer.objects.filter(question = current_question)
        
        correct_answers_texts = []
        for answer in correct_answers:
            correct_answers_texts.append(answer.answer_text)

        if user_answer in correct_answers_texts:
            print("You are correct")
            #Creates a new MODEL INSTANCE of CorrectlyAnswerQuestions
            correctly_answered_question = CorrectlyAnsweredQuestion()
            #Adds a new correctly answer question
            correctly_answered_question.question = current_question
            correctly_answered_question.user = User.objects.get(user_ldap = ldap)
            correctly_answered_question.save()
            go_to_next_quest(current_quest, current_user, current_project)

            return HttpResponseRedirect('/quest/user_quest_page/' + ldap + '/' + quest_id)

        print('You are wrong')
        return HttpResponseRedirect('/quest/user_quest_page/' + ldap + '/' + quest_id)
    
    return HttpResponseRedirect('/quest/user_quest_page/' + ldap + str(quest_id))


def validate_mc_question_response(request, ldap, quest_id):

    if not validate_user_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    current_quest = Quest.objects.get(id = quest_id)
    current_project = current_quest.project
    current_user = User.objects.get(user_ldap = ldap)
    

    if request.method == 'POST':
        #When do I check here whether the form is valid
        post_request = request.POST
        user_answer = post_request.getlist('answer')
        current_question = Question.objects.get(id = post_request['MC_response_id'])
        correct_answers = CorrectAnswer.objects.filter(question = current_question)


        correct_answers_texts = []
        for answer in correct_answers:
            correct_answers_texts.append(answer.answer_text)

        print (user_answer, correct_answers_texts)

        user_answer.sort()
        correct_answers_texts.sort()


        #Even if we need to select multiple answers to get the correct response, this will now work
        if user_answer == correct_answers_texts:
        #Creates a new MODEL INSTANCE of CorrectlyAnswerQuestions
            correctly_answered_question = CorrectlyAnsweredQuestion()
            #Adds a new correctly answer question
            correctly_answered_question.question = current_question
            correctly_answered_question.user = User.objects.get(user_ldap = ldap)
            correctly_answered_question.save()
            go_to_next_quest(current_quest, current_user, current_project)
            return HttpResponseRedirect('/quest/user_quest_page/' + ldap + '/' + quest_id)

        print('You are wrong')
        return HttpResponseRedirect('/quest/user_quest_page/' + ldap + '/' + quest_id)
        
    return HttpResponseRedirect('/quest/user_quest_page/' + ldap + str(quest_id))


######################################

#For editing free response questions (not creating)
def get_admin_edit_fr_question(request, ldap, question_id):

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    current_admin = Admin.objects.get(admin_ldap = ldap)
    current_question = Question.objects.get(id = question_id)
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
            return save_fr_question(ldap, question_form, answer_form, quest_id, timestamp)

    return HttpResponseRedirect('/quest/admin_edit_fr_question/' + ldap + '/' + str(question_id))





######################################
#For editing mc questions (not creating)
def get_admin_edit_mc_question(request, ldap, question_id):

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    current_admin = Admin.objects.get(admin_ldap = ldap)
    current_question = Question.objects.get(id = question_id)
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
            return save_mc_question(ldap, question_form, answer_form, wrong_answer_form, quest_id, timestamp)

    return HttpResponseRedirect('/quest/admin_edit_mc_question/' + ldap + '/' + str(question_id))

######################################

def get_admin_project_page(request, ldap):

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    project_form = ProjectForm()
    list_of_projects = Project.objects.all()
    current_admin = Admin.objects.get(admin_ldap = ldap)

    context = {'project_form': project_form, 'list_of_projects': list_of_projects, 'current_admin': current_admin}
    return render(request, 'quest_extension/admin_project_page.html', context)

def add_new_project(request, ldap):

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    current_admin = Admin.objects.get(admin_ldap = ldap)
    if request.method == 'POST':
        post_request = request.POST
        print(post_request)
        # form was submitted
        project_form = ProjectForm(request.POST)
        if project_form.is_valid():
            temp = project_form.save(commit=False)
            temp.project_editable = True
            temp.project_description = post_request['project_description']
            temp.save()
            project_id = temp.id    
            current_project = Project.objects.get(id = project_id) 
            new_admin_project = AdminProject()
            new_admin_project.admin = current_admin
            new_admin_project.project = current_project
            new_admin_project.save()
        
            return HttpResponseRedirect('/quest/admin_home_editable/'+ ldap + '/' + str(project_id))
    
    return HttpResponseRedirect('/quest/admin_project_page' + ldap)
    
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

    if request.method == 'POST':
        post_request = request.POST
        if 'random_phrase' in post_request.keys():
            inputted_random_phrase = post_request['random_phrase']
            project_requested = Project.objects.get(id = post_request['project_id'])


            if inputted_random_phrase == project_requested.project_random_phrase:
                new_user_project = UserProject()
                new_user_project.user = User.objects.get(user_ldap = ldap)
                new_user_project.project = project_requested

                #Decides what quest the user will begin on (not neccessary since now you can't edit a project after a user joins however - see other comment above)
                if len(Quest.objects.filter(project = project_requested, quest_path_number = 1)) == 1:
                    new_user_project.current_quest = Quest.objects.get(project = project_requested, quest_path_number = 1)
                else:
                    new_user_project.current_quest = None
                new_user_project.save() 
                #Since a user joined, the admin can no longer change the quest
                project_requested.project_editable = False
                project_requested.save()

            return HttpResponseRedirect('/quest/user_project_page/' + ldap)
    
    return HttpResponseRedirect('/quest/user_project_page/' + ldap)

def remove_user_project(request, ldap):

    if not validate_user_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    current_user = User.objects.get(user_ldap = ldap)
    
    if request.method == 'POST':
        post_request = request.POST
        #We aren't actually deleting the project, don't worry
        project_to_delete = Project.objects.get(id = post_request['remove_project'])

        user_project_to_delete = UserProject.objects.get(user = current_user, project= project_to_delete)
        user_project_to_delete.delete()
        
        quests = Quest.objects.filter(project = project_to_delete)
        questions = Question.objects.filter(quest__in= quests)
        correctly_answered_questions = CorrectlyAnsweredQuestion.objects.filter(user = current_user, question__in = questions)
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
        retyped_password = post_request['retyped_password']
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            temp = user_form.save(commit=False)
            email = temp.user_email
            user_ldap = temp.user_ldap

            try:
                validate_email(email)
                valid_email = True
            except:
                valid_email = False
                print("This is an invalid email")
                messages.success(request, 'Please input a valid email')
                return HttpResponseRedirect('/quest/new_user') 

            valid_password = (retyped_password == temp.user_password)
            new_ldap = user_ldap not in User.objects.all().values_list('user_ldap', flat=True) 
            print(User.objects.all().values_list('user_ldap', flat=True) )
            if valid_email and new_ldap and valid_password:
                temp.save()
                messages.success(request, 'Your new account was created!')
                return HttpResponseRedirect('/quest/user_login')
            if not new_ldap:
                messages.success(request, 'There is already an account associated with this LDAP')
            if not valid_password:
                messages.success(request, 'Your Password and Retyped Password do not match')

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
        password = post_request['password']
        print (post_request)

        if User.objects.filter(user_ldap = ldap):
            #If incorrect password
            if not User.objects.get(user_ldap = ldap).user_password == password:
                messages.success(request, 'Invalid Password')
            #If correct password for ldap - creates a session for the user
            else: 
                request.session['current_user_ldap'] = post_request['ldap']
                return HttpResponseRedirect('/quest/user_project_page/' + request.session['current_user_ldap'])
        #If LDAP is not associated with an account
        else:
            messages.success(request, 'There is no account associated with this LDAP')
    
    return HttpResponseRedirect('/quest/user_login')


def user_change_password_request(request):
    if request.method == 'POST':
        post_request = request.POST
        ldap = post_request['ldap']
        #only proceed if there is a user with this ldap
        if not User.objects.filter(user_ldap = ldap):
            messages.success(request, 'There is no account with this ldap')
            return HttpResponseRedirect('/quest/user_login')
        current_user = User.objects.get(user_ldap = ldap)
        if ldap not in User.objects.all().values_list('user_ldap', flat=True):
            messages.success(request, 'There is no account created for that LDAP')
        else:
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
            new_password = forgot_password_form.cleaned_data['new_password']
            retype_new_password = forgot_password_form.cleaned_data['retype_new_password']

            if (current_user.user_reset_password_pin != pin):
                messages.success(request,'Pin does not match the sent pin')
                return HttpResponseRedirect ('/quest/user_forgot_password/' + ldap)
            elif (new_password != retype_new_password):
                messages.success(request, 'Your Passwords do not match')
                return HttpResponseRedirect ('/quest/user_forgot_password/' + ldap)
            else:
                current_user.user_password = new_password
                #By setting this value to none as soon as possible, it leaves a very small window for
                #an intruder to try guessing the users pin
                current_user.user_reset_password_pin = None
                current_user.save()
                messages.success(request, 'Your new password was saved!')
                del request.session['current_user_ldap']
                return HttpResponseRedirect('/quest/user_login')

    return HttpResponseRedirect('/quest/user_forgot_password/' + ldap)

def go_back_to_login(request, ldap):
    if request.method == 'POST':
        current_user = User.objects.get(user_ldap = ldap)
        current_user.user_reset_password_pin = None
        current_user.save()
    return HttpResponseRedirect('/quest/user_login')

####################################

# def get_admin_edit_project_description(request, ldap, project_id):
#     current_project = Project.objects.get(id = project_id)
#     context = {'current_project': current_project}
#     return render(request, 'quest_extension/admin_edit_project_description.html', context)

def admin_update_project_description(request, ldap,  project_id):

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/admin_login')

    current_project = Project.objects.get(id = project_id)
    if request.method == 'POST':
        post_request = request.POST
        updated_project_description = post_request['project_description']
        current_project.project_description = updated_project_description
        current_project.save()
    return HttpResponseRedirect('/quest/admin_home_editable/' + ldap + '/' + str(project_id))
        

####################################

def get_user_info(request, ldap):
    
    if not validate_user_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    current_user = User.objects.get(user_ldap = ldap)
    context = {'current_user': current_user}
    return render(request, 'quest_extension/user_info.html', context)

def update_user_ldap(request, ldap):
    
    if not validate_user_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    current_user = User.objects.get(user_ldap = ldap)
    if request.method == 'POST':
        post_request = request.POST
        ldap_input = post_request['user_ldap']
        new_ldap = ldap_input not in User.objects.all().values_list('user_ldap', flat=True) 
        if (new_ldap):
            current_user.user_ldap = ldap_input
            current_user.save()
            request.session['current_user_ldap'] = ldap_input
            messages.success(request, 'Change was successful!')

        else:
             messages.success(request, 'There is already an account associated with this LDAP')


    
    return HttpResponseRedirect('/quest/user_info/' + current_user.user_ldap)

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


    return HttpResponseRedirect('/quest/user_info/' + current_user.user_ldap)

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

    return HttpResponseRedirect('/quest/user_info/' + current_user.user_ldap)

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
            messages.success(request, 'This is an invalid email')
    return HttpResponseRedirect('/quest/user_info/' + current_user.user_ldap)

def update_user_manager_ldap(request, ldap):
    if not validate_user_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    current_user = User.objects.get(user_ldap = ldap)
    if request.method == 'POST':
        post_request = request.POST
        user_manager_ldap_input = post_request['user_manager_ldap']
        current_user.user_manager_ldap = user_manager_ldap_input
        current_user.save()
        messages.success(request, 'Change was successful!')
    
    return HttpResponseRedirect('/quest/user_info/' + current_user.user_ldap)

def update_user_director_ldap(request, ldap):
    if not validate_user_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    current_user = User.objects.get(user_ldap = ldap)
    if request.method == 'POST':
        post_request = request.POST
        user_director_ldap_input = post_request['user_director_ldap']
        current_user.user_director_ldap = user_director_ldap_input
        current_user.save()
        messages.success(request, 'Change was successful!')

    
    return HttpResponseRedirect('/quest/user_info/' + current_user.user_ldap)

#We will need to do more with this one
def update_user_password(request, ldap):
    if not validate_user_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    current_user = User.objects.get(user_ldap = ldap)
    if request.method == 'POST':
        post_request = request.POST
        user_current_password = post_request['current_password']
        user_new_password = post_request['new_password']
        user_new_password_retyped = post_request['retyped_password']
        if user_current_password != current_user.user_password:
            messages.success(request, 'Your current password was typed incorrectly')
        if user_new_password != user_new_password_retyped:
            messages.success(request, 'Your new passwords do not match')
        else:
            current_user.user_password = user_new_password
            current_user.save()
            messages.success(request, 'Change was successful!')

    return HttpResponseRedirect('/quest/user_info/' + current_user.user_ldap)


    ####################################

def get_admin_project_info(request, ldap, project_id):
    
    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    current_admin = Admin.objects.get(admin_ldap = ldap)
    current_project = Project.objects.get(id = project_id)
    context = {'current_project': current_project, 'current_admin': current_admin}
    return render(request, 'quest_extension/admin_project_info.html', context)


def delete_project(request, ldap, project_id):

    if not validate_admin_access(request, ldap):
        return HttpResponseRedirect('/quest/user_login')

    if request.method == 'POST':
        current_project = Project.objects.get(id = project_id)
        current_project.delete()
        return HttpResponseRedirect('/quest/admin_project_page/' + ldap)
    return render(request, 'quest_extension/admin_project_info.html')


####################################

def get_admin_login(request):

    if 'current_admin_ldap' in request.session:
        del request.session['current_admin_ldap']

    login_form = LoginForm()
    context = {'login_form': login_form}
    return render(request, 'quest_extension/admin_login.html', context)

def admin_login_to_account(request):
    if request.method == 'POST':
        post_request = request.POST
        ldap = post_request['ldap']
        password = post_request['password']
        print (post_request)

        if Admin.objects.filter(admin_ldap = ldap):
            #If incorrect password
            if not Admin.objects.get(admin_ldap = ldap).admin_password == password:
                messages.success(request, 'Invalid Password')
            #If correct password for ldap
            else: 
                request.session['current_admin_ldap'] = post_request['ldap']
                return HttpResponseRedirect('/quest/admin_project_page/' + request.session['current_admin_ldap'])
        #If LDAP is not associated with an account
        else:
            messages.success(request, 'There is no Admin account associated with this LDAP')
    
    return HttpResponseRedirect('/quest/admin_login')

def admin_change_password_request(request):
    if request.method == 'POST':
        post_request = request.POST
        ldap = post_request['ldap']
        #only proceed if there is an Admin with this ldap
        if not Admin.objects.filter(admin_ldap = ldap):
            messages.success(request, 'There is no account with this ldap')
            return HttpResponseRedirect('/quest/admin_login')
        current_admin = Admin.objects.get(admin_ldap = ldap)
        if ldap not in Admin.objects.all().values_list('admin_ldap', flat=True):
            messages.success(request, 'There is no account created for that LDAP')
        else:
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
        retyped_password = post_request['retyped_password']
        admin_form = AdminForm(request.POST)
        if admin_form.is_valid():
            temp = admin_form.save(commit=False)
            email = temp.admin_email
            admin_ldap = temp.admin_ldap

            
            try:
                validate_email(email)
                valid_email = True
            except:
                valid_email = False
                print("This is an invalid email")
                messages.success(request, 'Please input a valid email')
                return HttpResponseRedirect('/quest/new_admin') 

            valid_password = (retyped_password == temp.admin_password)
            new_ldap = admin_ldap not in Admin.objects.all().values_list('admin_ldap', flat=True) 
            print(Admin.objects.all().values_list('admin_ldap', flat=True) )
            if valid_email and new_ldap and valid_password:
                temp.save()
                messages.success(request, 'Your new account was created!')
                return HttpResponseRedirect('/quest/admin_login')
            if not new_ldap:
                messages.success(request, 'There is already an account associated with this LDAP')
            if not valid_password:
                messages.success(request, 'Your Password and Retyped Password do not match')

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
            new_password = forgot_password_form.cleaned_data['new_password']
            retype_new_password = forgot_password_form.cleaned_data['retype_new_password']

            if (current_admin.admin_reset_password_pin != pin):
                messages.success(request,'Pin does not match the sent pin')
                return HttpResponseRedirect ('/quest/admin_forgot_password/' + ldap)
            elif (new_password != retype_new_password):
                messages.success(request, 'Your Passwords do not match')
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




