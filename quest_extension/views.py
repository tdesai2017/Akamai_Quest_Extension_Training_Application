from django.shortcuts import render
from django.http import HttpResponse
from quest_extension.models import *
from .forms import *
from django.http import HttpResponseRedirect
from django.utils.text import slugify
from django.utils.http import urlencode
from random import shuffle



def home(request):
    return render(request, 'quest_extension/home.html')
# Create your views here.

def quest_create(request):
    """creates a quest"""
    
    if request.method == 'POST':
        # form was submitted
        form = QuestForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/quest/admin_quest_page/' + request.POST['quest_name'])
    else:
        form = QuestForm()
    return render(request, 'quest_extension/test.html', {'form': form})


def create_fr_question(request, name):
    if request.method  == 'POST':
        #for was busmitted
        question_form = QuestionForm(request.POST)
        ans_form = CorrectAnswerForm(request.POST)
        if question_form.is_valid() and ans_form.is_valid():
            quest = Quest.objects.get(quest_name=name)
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
            
            return HttpResponseRedirect('/quest/admin_quest_page/' + name)
    else:
        form = QuestionForm()
        ans_form = CorrectAnswerForm()
    return render(request, 'quest_extension/fr_question_form.html', {'q_form' : form,
                                                         'ans_form' : ans_form})


def create_mc_question(request, name):
    if request.method  == 'POST':
        #for was submitted
        question_form = QuestionForm(request.POST)
        answer_form = RightAnswerForm(request.POST)
        wrong_answer_form = WrongAnswerForm(request.POST)
        
        if question_form.is_valid() and answer_form.is_valid() and wrong_answer_form.is_valid():
            quest = Quest.objects.get(quest_name=name)
            bbb = question_form.save(commit=False)
            bbb.question_type = 'MC'
            bbb.quest = quest
            bbb.save()
            question_id = bbb.id

            list_of_correct_answers = answer_form.cleaned_data['correct_choices'].split('\n')

            for correct_answer in list_of_correct_answers:
                #Stripping is not working
                correct_answer.strip()
                ccc = CorrectAnswer(question=Question.objects.get(id=question_id), answer_text= correct_answer)
                ccc.save()


            list_of_wrong_answers = wrong_answer_form.cleaned_data['incorrect_choices'].split('\n')

            for wrong_answer in list_of_wrong_answers:
                #Stripping is not working
                wrong_answer.strip()
                ddd = IncorrectAnswer(question=Question.objects.get(id=question_id), answer_text= wrong_answer)
                ddd.save()

            return HttpResponseRedirect('/quest/admin_quest_page/' + name)
    else:
        question_form = QuestionForm()
        answer_form = RightAnswerForm()
        wrong_answer_form = WrongAnswerForm()
    return render(request, 'quest_extension/mc_question_form.html', {'q_form' : question_form,
                                                                     'ans_form' : RightAnswerForm,
                                                                     'wrong_answer_form' : wrong_answer_form})


def admin_home(request):


    if request.method == 'POST':
        post_request = request.POST
        quest_form = QuestForm(post_request)
        if 'quest_description' in request.POST and 'quest_points_earned' in request.POST and 'quest_name' in request.POST:
           #make sure to make quest_name unique
            if quest_form.is_valid():
                quest_form.save()
                return HttpResponseRedirect('/quest/admin_quest_page/' + post_request['quest_name'])

    quests = Quest.objects.all()
    quest_form = QuestForm()
    context = {'quests':quests, 'quest_form': quest_form}
    return render(request, 'quest_extension/admin_home.html', context)

def admin_quest_page(request, name):

    current_quest = Quest.objects.get(quest_name = name)
    list_of_questions = Question.objects.filter(quest = current_quest)
    fr_input_form = TakeInFreeResponseForm

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

    context = {'current_quest': current_quest, 'format': format, 'fr_input_form': fr_input_form}
    return render(request, 'quest_extension/admin_quest_page.html', context)

def user_home(request, ldap):
    
    user = User.objects.get(user_ldap= ldap)

    # Figure out how we can replace this with Javascript
    if request.method == 'POST':
        post_request = request.POST

        # For some reason event though both evalued to the same number, 
        # they were always compared to be not equal to each other
        # That's why I am converting them both to strings
        if str(user.current_quest.quest_path_number) == str(post_request['quest_path_number']):

            current_quest = Quest.objects.get(quest_path_number = post_request['quest_path_number'])
            return HttpResponseRedirect('/quest/user_quest_page/' + user.user_ldap + "/" + current_quest.quest_name)

        else:
            return HttpResponseRedirect('/quest/user_home/' + ldap)

    quests = Quest.objects.all()
    context = {'quests':quests, 'user': user}
    return render(request, 'quest_extension/user_home.html', context)
    

def user_quest_page(request, ldap, name):

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
                return HttpResponseRedirect('/quest/user_home/' + ldap )

            print('You are wrong')
            return HttpResponseRedirect('/quest/user_quest_page/' + ldap + '/' + name)
        
        if 'MC_response_id' in post_request:
            user_answer = post_request.getlist('answer')
            current_question = Question.objects.get(id = post_request['MC_response_id'])
            correct_answers = CorrectAnswer.objects.filter(question = current_question)

            correct_answers_texts = []
            for answer in correct_answers:
                correct_answers_texts.append(answer.answer_text)

            user_answer.sort()
            correct_answers_texts.sort()


            print(user_answer) 
            print (correct_answers_texts)
            

            #Even if we need to select multiple answers to get the correct repsponse, this will now work
            if user_answer == correct_answers_texts:
                print("You are correct")
                return HttpResponseRedirect('/quest/user_home/' + ldap )

            print('You are wrong')
            return HttpResponseRedirect('/quest/user_quest_page/' + ldap + '/' + name)




    current_quest = Quest.objects.get(quest_name = name)
    list_of_questions = Question.objects.filter(quest = current_quest)
    fr_input_form = TakeInFreeResponseForm()


    format = {}
    for question in list_of_questions:
        correct_answer = CorrectAnswer.objects.filter(question = question)
        wrong_answers = IncorrectAnswer.objects.filter(question = question)
        all_answers = []

        for answer in wrong_answers:
            all_answers.append(answer)

        for answer in correct_answer:
            all_answers.append(answer)

        shuffle(all_answers)
        #Combines wrong answers with correct answer
        format[question] = all_answers 

    context = {'current_quest': current_quest, 'format': format, 'fr_input_form': fr_input_form, 'ldap': ldap}
    return render(request, 'quest_extension/user_quest_page.html', context)


def admin_edit_question(request, question_id):

    return HttpResponse("loopyschroopy")
