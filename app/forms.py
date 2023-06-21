from django import forms
from app import models
from django.contrib import auth
from django.utils.translation import gettext_lazy as _
from django.http import HttpRequest


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput(), max_length=80, min_length=6)


class EditForm(forms.ModelForm):
    username = forms.CharField(label="Nickname")
    email = forms.EmailField(label="Email")

    class Meta:
        model = models.Profile
        fields = ["username", "email", "avatar"]

    def save(self, user):
        email = self.cleaned_data.get('email')
        if user.email != email and auth.models.User.objects.filter(email=email):
            self.add_error(field=None, error="This email already exist")
            return False

        user.email = email

        username = self.cleaned_data.get('username')
        if len(username) < 3:
            self.add_error(field=None, error="Nickname is too short")
        if user.username != username and auth.models.User.objects.filter(username=username):
            self.add_error(field=None, error="This nickname already exist")
            return False

        user.username = username

        avatar = self.cleaned_data.pop('avatar')
        try:
            user.save()
        except Exception:
            self.add_error(field=None, error="Error")
            return False
        
        return self.cleaned_data



class RegisterForm(forms.ModelForm):
    username = forms.CharField(label="Nickname", max_length=30, min_length=3)
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput(), max_length=80, min_length=6)
    confirm_password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Repeat Password'}), max_length=80, min_length=6)

    class Meta:
        model = models.Profile
        fields = ["username", "email", "password",
                  "confirm_password", "avatar"]

    def save(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.pop('confirm_password')
        if password != confirm_password:
            self.add_error(
                field=None, error="Password and the confirmation password do not match")
            return False

        email = self.cleaned_data.get('email')
        if auth.models.User.objects.filter(email=email):
            self.add_error(field=None, error="This email already exist")
            return False

        username = self.cleaned_data.get('username')
        if auth.models.User.objects.filter(username=username):
            self.add_error(field=None, error="This nickname already exist")
            return False

        avatar = self.cleaned_data.pop('avatar')
        try:
            user = auth.models.User.objects.create_user(**self.cleaned_data)
            models.Profile.objects.create(
                user=user,
                avatar=avatar)
        except Exception as e:
            self.add_error(field=None, error="Error")
            return False
        return self.cleaned_data


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Enter tags'}), required=False)

    class Meta:
        model = models.Question
        fields = ['title', 'text', 'tags']

    def save(self, user):
        author = models.Profile.objects.get(user=user)
        tags = self.cleaned_data.pop('tags')
        tags = {
            models.Tag.objects.get_or_create(name=tag) for tag in set(tags.split(', ')) if tag != ""
        }
        question = models.Question.objects.create(
            author=author, **self.cleaned_data)
        for tag in tags:
            question.tags.add(tag[0])
            tag[0].count += 1
            tag[0].save()
        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = models.Answer
        fields = ['text']
        labels = {
            'text': "",
        }
        widgets = {
            'text' : forms.Textarea(
            attrs={"placeholder": "Enter your answer here...",}
        )
        }

    def save(self, user, question):
        author = models.Profile.objects.get(user=user)
        question.answers_count += 1
        question.save()
        return models.Answer.objects.create(
            author=author,
            question=question,
            **self.cleaned_data)
