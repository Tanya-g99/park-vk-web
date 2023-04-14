from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template import context
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from . import models


def index(request):
    base_context = {
        "popular_tags": models.Tag.objects.order_by_popular()[:6],
        "best_members": models.Profile.objects.all()[:5],
    }
    return render(request, 'index.html', context=(base_context | paginate(models.Question.objects.order_by_date(), request)))


def login(request):
    base_context = {
        "popular_tags": models.Tag.objects.order_by_popular()[:6],
        "best_members": models.Profile.objects.all()[:5],
    }
    return render(request, 'login.html', context=base_context)


def register(request):
    base_context = {
        "popular_tags": models.Tag.objects.order_by_popular()[:6],
        "best_members": models.Profile.objects.all()[:5],
    }
    return render(request, 'register.html', context=base_context)


def question(request, id: int):
    if (not models.Question.objects.filter(id=id).exists()) or id < 0:
        return render(request, "page404.html", status=404)

    base_context = {
        "popular_tags": models.Tag.objects.order_by_popular()[:6],
        "best_members": models.Profile.objects.all()[:5],
    }
    question_item = models.Question.objects.get_by_id(id)
    context = {"question": question_item} | paginate(
        models.Answer.objects.get_answers(question_item), request)
    return render(request, 'question.html', context=(context | base_context))


def tag_page(request, tag_name: str):
    if not models.Tag.objects.filter(name=tag_name).exists():
        return render(request, "page404.html", status=404)

    base_context = {
        "popular_tags": models.Tag.objects.order_by_popular()[:6],
        "best_members": models.Profile.objects.all()[:5],
    }
    context = {"tag": tag_name} | paginate(
        models.Question.objects.get_by_tag(tag_name), request)
    return render(request, "tag.html", context=(context | base_context))


def hot(request):
    base_context = {
        "popular_tags": models.Tag.objects.order_by_popular()[:6],
        "best_members": models.Profile.objects.all()[:5],
    }
    return render(request, 'hot.html', context=(base_context | paginate(models.Question.objects.order_by_rating(), request)))


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
