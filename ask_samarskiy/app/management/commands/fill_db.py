import random
from django.core.management.base import BaseCommand
from app.models import Profile, Question, Answer, Tag, Like
from django.contrib.auth.models import User
from datetime import datetime, timedelta


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def create_profiles(self, ratio):
        users = []
        profiles = []
        for i in range(ratio):
            username = f'user_{i}'
            rating = random.randint(1, 50)
            user = User(username=username, password='qwerty')
            users.append(user)
            profiles.append(Profile(user=user, rating=rating, image='static/img/profile.jpg'))  
        User.objects.bulk_create(users)  
        Profile.objects.bulk_create(profiles)  

    def create_tags(self, ratio):
        tags = [Tag(title=f'tag_{i}', index=i) for i in range(ratio)]
        Tag.objects.bulk_create(tags) 

    def create_questions(self, ratio):
        questions = []
        profiles = Profile.objects.all()
        tags = Tag.objects.all()
        for i in range(ratio):
            question = Question(
                title=f'Question title {i}',
                text='Question text.',
                author=random.choice(profiles),
                created_at = datetime.now() - timedelta(days=random.randint(0, 365)),
                likes=random.randint(-20, 20),
            )
            questions.append(question)
        Question.objects.bulk_create(questions) 
        for question in questions:
            tag_number = random.randint(1, 4)
            for i in range(tag_number):
                tag = random.choice(tags)
                question.tags.add(tag)

    def create_answers(self, ratio):
        answers = []
        questions = Question.objects.all()
        profiles = Profile.objects.all()
        for i in range(ratio):
            answer = Answer(
                title=f'Answer title {i}',
                text='Answer text.',
                question=random.choice(questions),
                author=random.choice(profiles),
                created_at=datetime.now() - timedelta(days=random.randint(0, 1825)),
                corect=random.choice([True, False]),
                likes=random.randint(-20, 20)
            )
            answers.append(answer)
        Answer.objects.bulk_create(answers) 

    def create_likes(self, ratio):
        qlikes = []
        alikes = []

        profiles = Profile.objects.all()
        questions = Question.objects.all()
        answers = Answer.objects.all()
        for i in range(ratio):
            question = random.choice(questions)
            qlikes.append(Like(author=random.choice(profiles),
                                       content_model=question,
                                       sign=True))
            i+=1
            if i == ratio: break
            answer = random.choice(answers)
            alikes.append(Like(author=random.choice(profiles),
                                     content_model=answer,
                                     sign=True))
        Like.objects.bulk_create(qlikes, ignore_conflicts=True)
        Like.objects.bulk_create(alikes, ignore_conflicts=True)  

    def handle(self, *args, **options):
        ratio = options['ratio']
        self.create_profiles(ratio)
        self.create_tags(ratio)
        self.create_questions(ratio * 10)
        self.create_answers(ratio * 100)
        self.create_likes(ratio * 200)