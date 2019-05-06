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






#Verifies that you are only trying to access the content for the ldap that you are logged in for
def validate_user_access(session_ldap, current_ldap):
    return (session_ldap == current_ldap)
        
    

#Checks whether you can go to the next question once you sumbit a new answer
def go_to_next_quest(current_quest, current_user, current_project):
    num_questions_in_quest = len(Question.objects.filter(quest = current_quest, deleted = False))
    all_questions_in_quest = [question for question in Question.objects.filter(quest = current_quest, deleted = False)]
    count_of_correctly_answered_questions = 0
    for question in all_questions_in_quest:
        if (CorrectlyAnsweredQuestion.objects.filter(question = question, user = current_user)):
            count_of_correctly_answered_questions += 1
            
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
            users_user_project_object.completed_project = True
            users_user_project_object.save()
            


#Views
def create_fr_question(request, quest_id):
    if request.method  == 'POST':
        
        question_form = QuestionForm(request.POST)
        ans_form = CorrectAnswerForm(request.POST)
        if question_form.is_valid() and ans_form.is_valid():
            quest = Quest.objects.get(id=quest_id)
            bbb = question_form.save(commit=False)
            bbb.question_type = 'FR'
            
            # if not bbb.question_text[len(bbb.question_text)-1] == '?':
            #     bbb.question_text += '?'


            bbb.quest = quest
            bbb.save()
            question_id = bbb.id

            ccc = ans_form.save(commit=False)
            ccc.question = Question.objects.get(id=question_id)
            ccc.save()
            
            return HttpResponseRedirect('/quest/admin_quest_page_editable/' + quest_id)
    else:
        form = QuestionForm()
        ans_form = CorrectAnswerForm()
    return render(request, 'quest_extension/fr_question_form.html', {'q_form' : form,
                                                         'ans_form' : ans_form})


def create_mc_question(request, quest_id):
    if request.method  == 'POST':
        #for was submitted
        question_form = QuestionForm(request.POST)
        answer_form = RightAnswerForm(request.POST)
        wrong_answer_form = WrongAnswerForm(request.POST)
        
        if question_form.is_valid() and answer_form.is_valid() and wrong_answer_form.is_valid():
            quest = Quest.objects.get(id=quest_id)
            bbb = question_form.save(commit=False)
            bbb.question_type = 'MC'
            bbb.quest = quest
            bbb.save()
            question_id = bbb.id

            list_of_correct_answers = answer_form.cleaned_data['correct_choices'].split('\n')


            for correct_answer in list_of_correct_answers:
                correct_answer = str(correct_answer).strip()
                ccc = CorrectAnswer(question=Question.objects.get(id=question_id), answer_text= correct_answer)
                ccc.save()
            


            list_of_wrong_answers = wrong_answer_form.cleaned_data['incorrect_choices'].split('\n')

            for wrong_answer in list_of_wrong_answers:
                wrong_answer = str(wrong_answer).strip()
                ddd = IncorrectAnswer(question=Question.objects.get(id=question_id), answer_text= wrong_answer)
                ddd.save()

            return HttpResponseRedirect('/quest/admin_quest_page_editable/' + quest_id)
    else:
        question_form = QuestionForm()
        answer_form = RightAnswerForm()
        wrong_answer_form = WrongAnswerForm()
    return render(request, 'quest_extension/mc_question_form.html', {'q_form' : question_form,
                                                                     'ans_form' : RightAnswerForm,
                                                                     'wrong_answer_form' : wrong_answer_form})


def admin_home_editable(request, project_id): 
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

                #The below part is unessary right now since admins cannot edit a proejct anymore after a user joins
                #it, however, I will keep it for now to prevent bugs

                # If a user has no current quest for a certain project since the admin never created a quest with path 1 until
                # now, the user's current quest will be updated here to the inputted quest with id = 1
                all_users_without_current_quests = UserProject.objects.filter(project = current_project, current_quest= None)
                if int(post_request['quest_path_number']) == 1 and len(all_users_without_current_quests) > 0:
                    print('Yes we made it here at least', len(all_users_without_current_quests))
                    for userproject in all_users_without_current_quests:
                        userproject.current_quest = temp
                        userproject.save()

                

                return HttpResponseRedirect('/quest/admin_quest_page_editable/' + str(quest_id))

    quests = Quest.objects.filter(project = current_project).order_by('quest_path_number')
    quest_form = QuestForm()
    context = {'quests':quests, 'quest_form': quest_form, 'current_project': current_project}
    return render(request, 'quest_extension/admin_home_editable.html', context)


def admin_home_view_only(request, project_id): 
    current_project = Project.objects.get(id = project_id)
    quests = Quest.objects.filter(project = current_project).order_by('quest_path_number')
    context = {'quests':quests, 'current_project': current_project}
    return render(request, 'quest_extension/admin_home_view_only.html', context)





def admin_quest_page_editable(request, quest_id):
    current_quest = Quest.objects.get(id = quest_id)
    current_project_id = current_quest.project.id


    if request.method == 'POST':
        post_request = request.POST
        if 'deleted' in post_request.keys():
            current_question = Question.objects.get(id = post_request['deleted'])
            print (post_request)
            current_question.deleted = True
            current_question.save()
            return HttpResponseRedirect('/quest/admin_quest_page_editable/' + str(current_question.quest.id))

        if 'undo' in post_request.keys():
            if Question.objects.filter(quest = current_quest, deleted = True):
                object_to_reappear = Question.objects.filter(quest = current_quest, deleted = True).latest('time_modified')
                object_to_reappear.deleted = False
                object_to_reappear.save()
            return HttpResponseRedirect(quest_id)


    list_of_questions = Question.objects.filter(quest = current_quest, deleted = False)
    fr_input_form = TakeInFreeResponseForm()

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

    context = {'current_quest': current_quest, 'format': format, 'fr_input_form': fr_input_form, 'current_project_id': current_project_id}
    return render(request, 'quest_extension/admin_quest_page_editable.html', context)


def admin_quest_page_view_only(request, quest_id):
    current_quest = Quest.objects.get(id = quest_id)
    current_project_id = current_quest.project.id
    list_of_questions = Question.objects.filter(quest = current_quest, deleted = False)
    fr_input_form = TakeInFreeResponseForm()

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

    context = {'current_quest': current_quest, 'format': format, 'fr_input_form': fr_input_form, 'current_project_id': current_project_id}
    return render(request, 'quest_extension/admin_quest_page_view_only.html', context)


def user_home(request, ldap, project_id):  
    if not validate_user_access(request.session['current_user_ldap'], ldap):
        return HttpResponseRedirect('/quest/user_login')
    user = User.objects.get(user_ldap= ldap)
    current_project = Project.objects.get(id = project_id)
    current_user_project_object = UserProject.objects.get(user = user, project = current_project)

    # Figure out how we can replace this with Javascript
    if request.method == 'POST':
        post_request = request.POST

        # For some reason event though both evalued to the same number, 
        # they were always compared to be not equal to each other
        # That's why I am converting them both to strings
        users_current_quest_path_num = str(UserProject.objects.get(user = user, project = current_project).current_quest.quest_path_number)
        if str(users_current_quest_path_num) >= str(post_request['quest_path_number']):
            quest_clicked_on = Quest.objects.get(quest_path_number = post_request['quest_path_number'], project = current_project)
            return HttpResponseRedirect('/quest/user_quest_page/' + user.user_ldap + "/" + str(quest_clicked_on.id))

        else:
            return HttpResponseRedirect('/quest/user_home/' + ldap + '/' + str(project_id))

    quests = Quest.objects.filter(project = current_project).order_by('quest_path_number')
    context = {'quests':quests, 'user': user, 'current_project': current_project, 'current_user_project_object': current_user_project_object}
    return render(request, 'quest_extension/user_home.html', context)
    

def user_quest_page(request, ldap, quest_id):
    if not validate_user_access(request.session['current_user_ldap'], ldap):
        return HttpResponseRedirect('/quest/user_login')

    current_quest = Quest.objects.get(id = quest_id)
    current_project_id = current_quest.project.id
    current_project = current_quest.project
    current_user = User.objects.get(user_ldap = ldap)


    if request.method == 'POST':
        #When do I check here whether the form is valid
        post_request = request.POST
        if 'FR_response_id' in post_request:
            user_answer = post_request['answer']
            current_question = Question.objects.get(id = post_request['FR_response_id'])
            correct_answers = CorrectAnswer.objects.filter(question = current_question)
            
            correct_answers_texts = []
            for answer in correct_answers:
                correct_answers_texts.append(answer.answer_text)

            if user_answer in correct_answers_texts:
                print("You are correct")
                correctly_answered_question = CorrectlyAnsweredQuestion()
                #Adds a new correctly answer question
                correctly_answered_question.question = current_question
                correctly_answered_question.user = User.objects.get(user_ldap = ldap)
                correctly_answered_question.save()
                go_to_next_quest(current_quest, current_user, current_project)

                return HttpResponseRedirect('/quest/user_quest_page/' + ldap + '/' + quest_id)

            print('You are wrong')
            return HttpResponseRedirect('/quest/user_quest_page/' + ldap + '/' + quest_id)
        
        if 'MC_response_id' in post_request:
            user_answer = post_request.getlist('answer')
            current_question = Question.objects.get(id = post_request['MC_response_id'])
            correct_answers = CorrectAnswer.objects.filter(question = current_question)

            correct_answers_texts = []
            for answer in correct_answers:
                correct_answers_texts.append(answer.answer_text)

            user_answer.sort()
            correct_answers_texts.sort()

            #Even if we need to select multiple answers to get the correct repsponse, this will now work
            if user_answer == correct_answers_texts:
                correctly_answered_question = CorrectlyAnsweredQuestion()
                #Adds a new correctly answer question
                correctly_answered_question.question = current_question
                correctly_answered_question.user = User.objects.get(user_ldap = ldap)
                correctly_answered_question.save()
                go_to_next_quest(current_quest, current_user, current_project)
                return HttpResponseRedirect('/quest/user_quest_page/' + ldap + '/' + quest_id)

            print('You are wrong')
            return HttpResponseRedirect('/quest/user_quest_page/' + ldap + '/' + quest_id)

    list_of_questions = Question.objects.filter(quest = current_quest, deleted=False)
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

    #Checks whether you can move onto the next quest, only happens when you give a post request for
    #the next answer
    
    context = {'current_quest': current_quest, 
            'format': format, 
            'fr_input_form': fr_input_form, 
            'ldap': ldap, 
            'current_project_id': current_project_id, 
            'have_correct_answer': have_correct_answer,
            'format_2': format_2}

    return render(request, 'quest_extension/user_quest_page.html', context)


def admin_edit_question(request, question_id):

    question_text_form = QuestionForm()
    mc_answer_form = RightAnswerForm()
    mc_wrong_answer_form = WrongAnswerForm()
    fr_answer_form = CorrectAnswerForm()
    
    
    current_question = Question.objects.get(id = question_id)
    print(current_question.question_type)
    context = {'current_question': current_question,
                'question_text_form': question_text_form,
                'mc_answer_form': mc_answer_form,
                'mc_wrong_answer_form': mc_wrong_answer_form,
                'fr_answer_form': fr_answer_form}
    return render(request, 'quest_extension/admin_edit_question.html', context)

def admin_project_page(request):

    if request.method == 'POST':
        # form was submitted
        project_form = ProjectForm(request.POST)
        if project_form.is_valid():
            temp = project_form.save(commit=False)
            temp.project_editable = True
            temp.save()
            project_id = temp.id

            return HttpResponseRedirect('/quest/admin_home_editable/' + str(project_id))
    else:
        project_form = ProjectForm()
        list_of_projects = Project.objects.all()

    context = {'project_form': project_form, 'list_of_projects': list_of_projects}
    return render(request, 'quest_extension/admin_project_page.html', context)

def user_project_page(request, ldap):

    current_user = User.objects.get(user_ldap = ldap)
    user_projects = [user_project.project for user_project in UserProject.objects.filter(user = current_user)]
    user_project_ids = [project.id for project in user_projects]
    all_other_projects = [project for project in Project.objects.all() if project.id not in user_project_ids]
    add_new_project_form = AddNewProjectForm()

    if not validate_user_access(request.session['current_user_ldap'], ldap):
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

        if 'logout' in post_request.keys():
            del request.session['current_user_ldap']
            return HttpResponseRedirect('/quest/user_login')

        if 'remove_project' in post_request.keys():

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


        
    context = {'current_user': current_user,
     'user_projects': user_projects,
      'all_other_projects': all_other_projects,
      'add_new_project_form': add_new_project_form}
    return render(request, 'quest_extension/user_project_page.html', context)

def new_user(request):
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

            new_ldap = user_ldap not in [user.user_ldap for user in User.objects.all()]
            

            if valid_email and new_ldap:
                temp.save()
                return HttpResponseRedirect('/quest/user_login')
            else:
                messages.success(request, 'There is already an account associated with this LDAP')


            

    user_form = UserForm()
    context = {'user_form': user_form}
    return render(request, 'quest_extension/new_user.html', context)

def user_login (request):
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

       

    
    login_form = LoginForm()
    context = {'login_form': login_form}
    return render(request, 'quest_extension/user_login.html', context)





            


