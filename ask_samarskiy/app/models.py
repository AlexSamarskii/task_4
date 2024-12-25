from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count


class ProfileManager(models.Manager):
    def best(self):
        return self.order_by('-rating')[:5]

class Profile(models.Model):
    objects = ProfileManager()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='static/img/', default='profile.jpg')
    rating = models.IntegerField(default=0)

class TagManager(models.Manager):
    def most_popular(self):
        return self.annotate(quest_count=Count('question')).order_by('-quest_count')[:10]
        

class Tag(models.Model):
    objects = TagManager()
    title = models.CharField(max_length=50)
    index = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.title

class QuestionManager(models.Manager):
    def by_tag(self, tag_name):
        return self.filter(tags__title=tag_name).all()
    
    def new(self):
        return self.order_by('-created_at')
    
    def hot(self):
        return self.order_by('-likes')
    
            
class Question(models.Model):
    objects = QuestionManager()
    title = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
        
    def __str__(self):
        return self.title
    
    def liked(self, user, sign):
        liked = Like.objects.filter(author=user, content_model=self)
        if(liked==0):
            Like.objects.add(author=user, content_type=self, sign=sign)
            if sign == True:
                self.liked+=1
            else: self.liked-=1
    

class AnswerManager(models.Manager):
    def answers_for_question(self, quest):
        return self.filter(question=quest).all()

class Answer(models.Model):
    objects = AnswerManager()
    title = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    corect = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return self.title
    
    def liked(self, user, sign):
        liked = Like.objects.filter(author=user, content_type=self)
        if(liked==0):
            Like.objects.add(author=user, content_model=self, sign=sign)
            if sign == True:
                self.liked+=1
            else: self.liked-=1
            

class LikeManager(models.Manager):
    pass
        
class Like(models.Model):
    object_id = models.PositiveIntegerField(default=0)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_model = GenericForeignKey("content_type", "object_id")
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    sign = models.BooleanField(default=True)

