from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import context
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from . import models
from .forms import LoginForm, RegisterForm, QuestionForm, AnswerForm, EditForm
from django.contrib import auth


def index(request):
    base_context = {
        "popular_tags": models.Tag.objects.order_by_popular()[:10],
        "best_members": models.Profile.objects.all()[:5],
    }
    return render(request, 'index.html', context=(base_context | paginate(models.Question.objects.order_by_date(), request)))


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    


def ask(request: HttpRequest):
    base_context = {
        "popular_tags": models.Tag.objects.order_by_popular()[:10],
        "best_members": models.Profile.objects.all()[:5],
    }

    if request.method == "POST":
        if request.user.is_authenticated:
            form = QuestionForm(request.POST)
            if form.is_valid():
                new_question = form.save(request.user)
                if new_question:
                    return HttpResponseRedirect("/")
                    
    else:
        if request.user.is_authenticated:
            form = QuestionForm()
        else:
            form = LoginForm()
            return render(request, 'login.html', context=(base_context | {"form": form}))

    return render(request, 'ask.html', context=(base_context | {"form": form}))


def login(request: HttpRequest):
    base_context = {
        "popular_tags": models.Tag.objects.order_by_popular()[:10],
        "best_members": models.Profile.objects.all()[:5],
    }
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user_by_email = auth.models.User.objects.filter(email=email)
            if user_by_email:
                user = auth.authenticate(request, username=user_by_email[0].username, **form.cleaned_data)
                if user:
                    auth.login(request, user)
                    return HttpResponseRedirect(request.GET.get('continue'))
                
            form.add_error(field=None, error="User not found")

    else:
        form = LoginForm()
    return render(request, 'login.html', context=(base_context | {"form": form}))


def register(request: HttpRequest):
    base_context = {
        "popular_tags": models.Tag.objects.order_by_popular()[:10],
        "best_members": models.Profile.objects.all()[:5],
    }

    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            new_user = form.save()
            if new_user:
                user = auth.authenticate(request, **new_user)
                auth.login(request, user)
                return HttpResponseRedirect("/")
        else:
            form.add_error(field=None, error="Please enter a valid data")
    else:
        form = RegisterForm()
    return render(request, 'register.html', context=(base_context | {"form": form}))


def question(request: HttpRequest, id: int):
    if (not models.Question.objects.filter(id=id).exists()) or id < 0:
        return render(request, "page404.html", status=404)

    base_context = {
        "popular_tags": models.Tag.objects.order_by_popular()[:10],
        "best_members": models.Profile.objects.all()[:5],
    }
    question_item = models.Question.objects.get_by_id(id)
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = AnswerForm(request.POST)
            if form.is_valid():
                answer = form.save(request.user, question_item)
                return HttpResponseRedirect(request.path)
            else:
                form.add_error(field=None, error="Please enter an answer")
        else:
            return HttpResponseRedirect("/login?continue=/ask")
    else:
        form = AnswerForm()
    context = {"question": question_item, "form": form} | paginate(
        models.Answer.objects.get_answers(question_item), request)
    return render(request, 'question.html', context=(context | base_context))


def tag_page(request: HttpRequest, tag_name: str):
    if not models.Tag.objects.filter(name=tag_name).exists():
        return render(request, "page404.html", status=404)

    base_context = {
        "popular_tags": models.Tag.objects.order_by_popular()[:10],
        "best_members": models.Profile.objects.all()[:5],
    }
    context = {"tag": tag_name} | paginate(
        models.Question.objects.get_by_tag(tag_name), request)
    return render(request, "tag.html", context=(context | base_context))


def hot(request: HttpRequest):
    base_context = {
        "popular_tags": models.Tag.objects.order_by_popular()[:10],
        "best_members": models.Profile.objects.all()[:5],
    }
    return render(request, 'hot.html', context=(base_context | paginate(models.Question.objects.order_by_rating(), request)))


def edit(request: HttpRequest):
    base_context = {
        "popular_tags": models.Tag.objects.order_by_popular()[:10],
        "best_members": models.Profile.objects.all()[:5],
    }
    if request.method == 'POST':
        form = EditForm(request.POST, request.FILES)
        if form.is_valid():
            new_user = form.save(request.user)
        else:
            form.add_error(field=None, error="Please enter a valid data")
    else:
        if request.user.is_authenticated:
            form = EditForm(initial={
            'username': request.user.username,
            'email': request.user.email,
            })
        else:
            form = LoginForm()
            return render(request, 'login.html', context=(base_context | {"form": form}))
        
    return render(request, 'profile_edit.html', context=(base_context | { "form": form }))


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get("page") or 1
    page_obj = paginator.get_page(page_number)
    result = {
        "page_obj": page_obj,
        "ELLIPSIS": paginator.ELLIPSIS,
        "elided_page_range": []
    }
    try:
        result["elided_page_range"] = [
            p for p in paginator.get_elided_page_range(
                number=page_number, on_each_side=2, on_ends=1)]
    except (PageNotAnInteger, EmptyPage):
        result["elided_page_range"] = [
            p for p in paginator.get_elided_page_range(
                number=paginator.num_pages, on_each_side=2, on_ends=1)]
    return result
