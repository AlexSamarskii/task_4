import copy
from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from app.models import Question, Answer, Tag, Like, Profile
from app.forms import LoginForm, RegisterForm, AskForm, AnswerForm, ProfileForm
from django.contrib.auth.decorators import login_required

# ANSWERS = [
#     {
# 'title': f'Answer {i}',
# 'text': f'Text for answer # {i}',
# 'id': i,
#     } for i in range(10)
# ]
# TAGS = [
#     {
# 'title': f'tag{i}',
# 'index': i
#     } for i in range(10)
# ] 
# QUESTIONS = [
#     {
# 'title': f'Title {i}',
# 'id': i,
# 'text': f'Text for question # {i}',
# 'tags': [TAGS[1], TAGS[5] , TAGS[(i%10)]],
# 'answers': ANSWERS
#     } for i in range(30)
# ]
styles = [
                'text-bg-primary', 'text-bg-secondary', 'text-bg-success', 'text-bg-danger',
                'text-bg-warning', 'text-bg-info', 'text-bg-light', 'text-bg-dark'
        ]

fixed = {'best_profiles': Profile.objects.best(), 
            'popular_tags': [[tag, style] for tag, style in zip(Tag.objects.most_popular(), styles)]
}

def paginator(object_list, request, per_page=10):
    required_page = []
    paginator = Paginator(object_list, per_page)
    num_pages = paginator.num_pages
    page = request.GET.get('page')
    try:
        required_page = paginator.get_page(page)
    except PageNotAnInteger:
        required_page = paginator.get_page(1)
    except EmptyPage:
        if(required_page < 1):
            required_page = paginator.get_page(1)
        elif(required_page > num_pages):
            required_page = paginator.get_page(num_pages)
    return required_page    
           

def index(request):
    return render(request, template_name="index.html",
                  context={'questions': paginator(Question.objects.new(), request)} | fixed)

def hot(request):
    return render(request, template_name="hot.html",
                  context={'questions': paginator(Question.objects.hot(), request)} | fixed)
    
    
def question(request, question_id):
    one_question = get_object_or_404(Question, pk=question_id)
    answers = paginator(Answer.objects.answers_for_question(question_id), request, 5)
    return render(request, template_name="one-question.html",
                  context={'question': one_question,
                           'answers': answers} | fixed)

def question_form(request, question_id):
    form = AnswerForm(request.user, question_id)
    question = get_object_or_404(Question, pk=question_id)
    answers = paginator(Answer.objects.answers_for_question(question_id), request)
    if request.POST:
        form = AnswerForm(request.user, question_id, request.POST)
        if not request.user.is_authenticated:
            return redirect('login')
        if form.is_valid():
            form.save()
            return redirect(reverse('one_question', args=[question_id]) + f'?page={1}')
    return render(request, 'one-question.html', context={'question': question,
                    'answers': answers,
                    'form': form} | fixed)

                     
def login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(request, **form.cleaned_data)
            if user:
                auth.login(request, user)
                return redirect(request.GET.get('continue', 'index'))
            else:
                form.add_error(None, error='Invalid username or password')
    return render(request, template_name='login.html', 
                    context={'form': form} | fixed)
    
def logout(request):
    auth.logout(request)
    return redirect('index')

def signup(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user:
                auth.login(request, user)
                return redirect('index')
        else:
            print(form.errors)
    return render(request, 'signup.html', context={'form': form} | fixed)
    
# def ask(request):
#     form = AskForm(request.POST)
#     if request.method.POST:
#         pass
#     return render(request, template_name='ask.html',
#                      context={'title': 'New Question'} | fixed)
    
@login_required(login_url="/login/")
def ask_form(request):
    form = AskForm(request.user)
    if request.POST:
        form = AskForm(request.user, request.POST)
        if form.is_valid():
            question = form.save()
            return redirect('one_question', question_id=question.id)
    return render(request, 'ask.html', context={'form': form} | fixed)


@login_required(login_url='/login/')
def profile(request):
    form = ProfileForm(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            return redirect('profile')
    return render(request, 'profile.html', context={'form': form} | fixed)
    

# def profile_edit(request):
#     form = ProfileForm
#     if request.method == 'POST':
#         form = ProfileForm(request.POST, instance=request.user.profile, user=request.user)
#         if form.is_valid():
#             form.save()
#             auth.login(request, request.user)
#             return redirect('profile_edit')
#     return render(request, 'profile.html', {'form': form} | fixed)
   
    
def tag(request, tag_name):
    tag = Tag.objects.get(title=tag_name)
    return render(request, 'tag.html',
                  context={'tag': tag, 'questions': paginator(Question.objects.by_tag(tag_name), request)} | fixed)


 