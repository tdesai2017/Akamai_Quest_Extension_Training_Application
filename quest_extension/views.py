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

#Views


def get_fr_question_form(request, quest_id):
        question_form = QuestionForm()
        answer_form = CorrectAnswerForm()
        context = {'q_form' : question_form, 'ans_form' : answer_form, 'quest_id': quest_id}
        return render(request, 'quest_extension/fr_question_form.html', context )

def create_fr_question(request, quest_id):
    if request.method  == 'POST':
        
        question_form = QuestionForm(request.POST)
        answer_form = CorrectAnswerForm(request.POST)
        if question_form.is_valid() and answer_form.is_valid():
            return save_fr_question(question_form, answer_form, quest_id)
    
    return HttpResponseRedirect('/quest/fr-create-form/' + str(quest_id))
    
    
######################################

def get_mc_question_form(request, quest_id):

    question_form = QuestionForm()
    answer_form = RightAnswerForm()
    wrong_answer_form = WrongAnswerForm()
    context = {'q_form' : question_form, 'ans_form' : answer_form, 'wrong_answer_form' : wrong_answer_form, 'quest_id': quest_id}
    return render(request, 'quest_extension/mc_question_form.html', context)


def create_mc_question(request, quest_id):
    if request.method  == 'POST':
        question_form = QuestionForm(request.POST)
        answer_form = RightAnswerForm(request.POST)
        wrong_answer_form = WrongAnswerForm(request.POST)
        if question_form.is_valid() and answer_form.is_valid() and wrong_answer_form.is_valid():
            return save_mc_question(question_form, answer_form, wrong_answer_form, quest_id)
        
    return HttpResponseRedirect('/quest/mc-create-form/' + str(quest_id))


######################################


def get_admin_home_editable(request, project_id): 
    current_project = Project.objects.get(id = project_id)
    quests = Quest.objects.filter(project = current_project).order_by('quest_path_number')
    quest_form = QuestForm()
    context = {'quests':quests, 'quest_form': quest_form, 'current_project': current_project}
    return render(request, 'quest_extension/admin_home_editable.html', context)

def save_new_quest(request, project_id): 
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

                return HttpResponseRedirect('/quest/admin_quest_page_editable/' + str(quest_id))

    return HttpResponseRedirect('/quest/admin_home_editable/' + str(project_id))

######################################


def get_admin_home_view_only(request, project_id): 
    current_project = Project.objects.get(id = project_id)
    quests = Quest.objects.filter(project = current_project).order_by('quest_path_number')
    context = {'quests':quests, 'current_project': current_project}
    return render(request, 'quest_extension/admin_home_view_only.html', context)

######################################

def get_admin_quest_page_editable(request, quest_id):
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
     'all_videos': all_videos}
    return render(request, 'quest_extension/admin_quest_page_editable.html', context)


def delete_question(request, quest_id):

    if request.method == 'POST':
        post_request = request.POST
        current_question = Question.objects.get(id = post_request['deleted'])
        print (post_request)
        #We want to not let the time_modified increase, so we save it here and assign it to the question after we save it
        current_time_modified = copy.deepcopy(current_question.time_modified)
        current_question.deleted = True
        current_question.save()
        Question.objects.filter(id = post_request['deleted']).update(time_modified = current_time_modified)

    return HttpResponseRedirect('/quest/admin_quest_page_editable/' + str(quest_id))

def undo_delete_question(request, quest_id):
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

    return HttpResponseRedirect('/quest/admin_quest_page_editable/' + str(quest_id))


def save_video(request, quest_id):
    current_quest = Quest.objects.get(id = quest_id)
    if request.method == 'POST': 
        post_request = request.POST
        video_form = VideoForm(post_request)
        print(video_form)
        if video_form.is_valid():
            temp = video_form.save(commit=False)   
            url = post_request['video_url']
            if "v=" not in url or len(url) <= 2:
                    return HttpResponseRedirect('/quest/admin_quest_page_editable/' + str(quest_id))

            video_identifier = url[url.index('v=') + 2]
            temp.video_url = video_identifier
            temp.quest = current_quest
            temp.save()
            
    return HttpResponseRedirect('/quest/admin_quest_page_editable/' + str(quest_id))


def delete_video(request, quest_id):
    current_quest = Quest.objects.get(id = quest_id)
    if request.method == 'POST': 
        post_request = request.POST
        video_id = post_request['delete']
        video_to_delete = Video.objects.get(id = video_id)
        print("YOU ARE HERE", video_to_delete)
        video_to_delete.delete()
            
    return HttpResponseRedirect('/quest/admin_quest_page_editable/' + str(quest_id))



        



######################################

def get_admin_quest_page_view_only(request, quest_id):
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

    context = {'current_quest': current_quest, 'format': format, 'fr_input_form': fr_input_form, 'current_project_id': current_project_id, 'all_videos': all_videos}
    return render(request, 'quest_extension/admin_quest_page_view_only.html', context)

######################################

def get_user_home(request, ldap, project_id):
    if not validate_user_access(request.session['current_user_ldap'], ldap):
        return HttpResponseRedirect('/quest/user_login')

    user = User.objects.get(user_ldap= ldap)
    current_project = Project.objects.get(id = project_id)
    current_user_project_object = UserProject.objects.get(user = user, project = current_project)
    quests = Quest.objects.filter(project = current_project).order_by('quest_path_number')
    context = {'quests':quests, 'user': user, 'current_project': current_project, 'current_user_project_object': current_user_project_object}
    return render(request, 'quest_extension/user_home.html', context)


######################################

def get_user_quest_page(request, ldap, quest_id):
    if not validate_user_access(request.session['current_user_ldap'], ldap):
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
    
    return HttpResponseRedirect('/quest/user_quest_page' + ldap + str(quest_id))


def validate_mc_question_response(request, ldap, quest_id):

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
        
    return HttpResponseRedirect('/quest/user_quest_page' + ldap + str(quest_id))


######################################

def admin_edit_fr_question(request, question_id):

    current_question = Question.objects.get(id = question_id)
    current_questions_answers = CorrectAnswer.objects.filter(question = current_question)
    question_text_form = QuestionForm(initial={'question_text': current_question.question_text})

    all_answers = ""
    for answer in current_questions_answers:
        answer_text = answer.answer_text
        all_answers += (answer_text + " ")

    fr_answer_form = CorrectAnswerForm(initial={'answer_text': all_answers})

    
    print (all_answers)

    if request.method == 'POST':
        post_request = request.POST
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
            return save_fr_question(question_form, answer_form, quest_id, timestamp)


    
    current_question = Question.objects.get(id = question_id)
    print(current_question.question_type)
    context = {'current_question': current_question,
                'question_text_form': question_text_form,
                'fr_answer_form': fr_answer_form}
    return render(request, 'quest_extension/admin_edit_fr_question.html', context)



######################################
def get_edit_mc_question(request, question_id):

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
                'quest_id': quest_id}
    return render(request, 'quest_extension/admin_edit_mc_question.html', context)
    
def save_edit_mc_question (request, question_id):
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
            return save_mc_question(question_form, answer_form, wrong_answer_form, quest_id, timestamp)

    return HttpResponseRedirect('/quest/admin_edit_mc_question' + str(question_id))

######################################

def get_admin_project_page(request):
    project_form = ProjectForm()
    list_of_projects = Project.objects.all()

    context = {'project_form': project_form, 'list_of_projects': list_of_projects}
    return render(request, 'quest_extension/admin_project_page.html', context)

def add_new_project(request):

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

            return HttpResponseRedirect('/quest/admin_home_editable/' + str(project_id))
    
    return HttpResponseRedirect('/quest/admin_project_page')
    
######################################
def get_user_project_page(request, ldap):

    if not validate_user_access(request.session['current_user_ldap'], ldap):
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

    if request.method == 'POST':
        del request.session['current_user_ldap']
        return HttpResponseRedirect('/quest/user_login')

    return HttpResponseRedirect('/quest/user_project_page' + ldap)


def add_user_project_page(request, ldap):

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
    
    return HttpResponseRedirect('/quest/user_project_page' + ldap)

def remove_user_project(request, ldap):

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
    return HttpResponseRedirect('/quest/user_project_page' + ldap)

######################################


def get_new_user_page(request):

    user_form = UserForm()
    context = {'user_form': user_form}
    return render(request, 'quest_extension/new_user.html', context)

def add_new_user(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            temp = user_form.save(commit=False)
            username = temp.user_email
            user_ldap = temp.user_ldap
            #I feel like this is really slow and want to figure out a faster way, since right now
            #This will have to iterate through every person -> figure out a way to make this faster
            try:
                validate_email(username)
                valid_email = True
            except:
                valid_email = False
                print("This is an invalid email")
                messages.success(request, 'Please input a valid email')
                return HttpResponseRedirect('/quest/new_user') 

            #Use filter for this - django ORM
            new_ldap = user_ldap not in [user.user_ldap for user in User.objects.all()]
            print(new_ldap)
            if valid_email and new_ldap:
                temp.save()
                return HttpResponseRedirect('/quest/user_login')
            else:
                messages.success(request, 'There is already an account associated with this LDAP')

    return HttpResponseRedirect('/quest/new_user')

######################################

def get_user_login(request):

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
            #If correct password for ldap
            else: 
                request.session['current_user_ldap'] = post_request['ldap']
                return HttpResponseRedirect('/quest/user_project_page/' + request.session['current_user_ldap'])
        #If LDAP is not associated with an account
        else:
            messages.success(request, 'There is no account associated with this LDAP')
    
    return HttpResponseRedirect('/quest/user_login')


####################################

def get_admin_edit_project_description(request, project_id):
    current_project = Project.objects.get(id = project_id)
    context = {'current_project': current_project}
    return render(request, 'quest_extension/admin_edit_project_description.html', context)

def admin_update_project_description(request, project_id):
    current_project = Project.objects.get(id = project_id)
    if request.method == 'POST':
        post_request = request.POST
        updated_project_description = post_request['project_description']
        current_project.project_description = updated_project_description
        current_project.save()
        print('IA M HERE')
        return HttpResponseRedirect('/quest/admin_home_editable/' + str(project_id))
        
    return HttpResponseRedirect('/quest/get_admin_edit_project_description' + str(project_id))