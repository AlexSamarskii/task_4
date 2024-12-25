from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from app.models import Profile, Question, Answer, Tag
import re


class LoginForm(forms.Form):
    username = forms.CharField(min_length=5, max_length=30,
        label='Login',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(min_length=5,
        max_length=30,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    def clean_login(self):
        username = self.cleaned_data.get('login')
        if len(username.strip()) < 5:
            self.add_error('login', 'Non valid login')
        return username.strip()
    
            
    
class RegisterForm(forms.Form):
    username = forms.CharField(min_length=5, max_length=30, required=True,
        label='Login',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(min_length=5, max_length=50, required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(min_length=5, max_length=30, required=True,
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password_confirmation = forms.CharField(min_length=5, max_length=30, required=True,
        label='Confirm password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    def clean_login(self):
        data = super().clean()
        username = data.get('username')
        _username = User.objects.filter(username=username)
        if _username.exists():
            raise ValidationError('The user with this login already exists')
        return username
    
    def clean_email(self):
        data = super().clean()
        email = data.get('email')
        _email = User.objects.filter(email=email)
        if _email.exists():
            raise ValidationError('The user with this email already exists')
        return email
    
    def clean_password_confirmation(self):
        # data = super().clean()
        # password = data.get('passsword')
        # password_confirm = data.get('password_confirmation')
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirmation')
        if password != password_confirm:
            raise ValidationError('Passwords don\'t match')
        return password_confirm
    
    
    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data.get('username'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('password')
        )
        Profile.objects.create(user=user)
        return user


class AskForm(forms.Form):
    title = forms.CharField(max_length=200, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    text = forms.CharField(max_length=500,
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )
    tags = forms.CharField(max_length=100,
        required=False, widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    class Meta:
        models = Question
        fields = ['title', 'text', 'tags']
     
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise ValidationError('Your title is shorter 5 symbols')
        return title
    
    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) < 10:
            raise ValidationError('Your ask is shorter 10 symbols')
        return text
    
    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
        if len(tags) > 20:
            raise ValidationError('Adding more 20 tags')
        return tags
    
    def save(self, commit=True):
        author = Profile.objects.get(user=self.user)
        title = self.cleaned_data.get('title')
        text = self.cleaned_data.get('text')
        question = Question(
            author=author,
            title=title,
            text=text
        )
        if commit:
            question.save()
            tags = self.cleaned_data.get('tags', [])
            tags = set(tags)
            for _tag in tags:
                tag, created = Tag.objects.get_or_create(title=_tag.lower().strip())
                question.tags.add(tag)
        return question 
    
class AnswerForm(forms.Form):
    text = forms.CharField(max_length=500, required=True, label='Add your answer',
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Answer
        fields=['text']
        
    def __init__(self, user, question_id, *args, **kwargs):
        self.user = user
        self.question_id = question_id
        super().__init__(*args, **kwargs)
    
    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) < 20:
            raise ValidationError('Your answer is shorter 20 symbols')
        return text
    
    def save(self, commit=True):
        question = Question.objects.get(pk=self.question_id)
        author = Profile.objects.get(user=self.user)
        answer = Answer(author=author, question=question, text=self.cleaned_data['text'])
        if commit:
            question.save()
            answer.save()
        return answer

    
class ProfileForm(forms.Form):
    username = forms.CharField(min_length=10, max_length=40,
        required=True, label='Login',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(min_length=10, max_length=40,
        required=True, label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(min_length=10, max_length=30,
        required=True, label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    password_confirmation = forms.CharField(min_length=10, max_length=30,
        required=True, label='Password Confirmation',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        
    def clean_login(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username) and username.filter(pk=self.user.pk).exists():
            raise ValidationError('The user with this login already exists')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email) and email.filter(pk=self.user.pk).exists():
            raise ValidationError('The user with this email already exists')
        return email

    def clean_password_confirmation(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirmation')
        if password and password != password_confirm:
            raise ValidationError('Passwords don\'t match')
        return password_confirm

    def save(self, commit=True):
        user = super().save()
        user.username = self.cleaned_data.get('username')
        user.email = self.cleaned_data.get('email')
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data.get('password'))

        profile = user.profile
        if commit:
            user.save()
            profile.save()

        return user
