from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='', blank=True, null=True, default='profile.jpg')

    def __str__(self):
        return self.user.username

    def email(self):
        return self.user.email


class TagManager(models.Manager):
    def order_by_popular(self):
        return self.order_by('-count')


class Tag(models.Model):
    name = models.CharField(max_length=25, unique=True)
    color = models.CharField(max_length=13, default="33, 10, 230")
    count = models.IntegerField(default=0)
    objects = TagManager()

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def order_by_date(self):
        return self.order_by('-creation_date')

    def order_by_rating(self):
        return self.order_by('-rating', '-answers_count')

    def get_by_tag(self, tag):
        return self.filter(tags__name__icontains=tag)

    def get_by_id(self, id):
        return self.get(pk=id)


class Question(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    text = models.TextField(max_length=1000, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    rating = models.IntegerField(default=0)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False)
    answers_count = models.IntegerField(default=0)
    objects = QuestionManager()

    def __str__(self):
        return self.title


class QuestionGrade(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.BooleanField()
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)


class AnswerManager(models.Manager):
    def get_answers(self, question):
        return self.filter(question=question).order_by('-rating')


class Answer(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField(max_length=1000)
    rating = models.IntegerField(default=0)
    correct = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False)
    objects = AnswerManager()


class AnswerGrade(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    value = models.BooleanField()
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
