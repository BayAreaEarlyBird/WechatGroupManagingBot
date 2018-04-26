from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from datetime import date, timedelta

from .models import User, History
from .utils import parse_solved_problems, get_last_history, update_history


def index(request):
    return HttpResponse('Hello, World')


@csrf_exempt
def register(request):
    if request.method == 'POST':
        user = User()
        user.username = request.POST.get('username', None)
        user.url = request.POST.get('url', None)
        solved_problems = parse_solved_problems(user.url)
        if solved_problems:
            try:
                user.save()
                history = History()
                history.solved_problems = solved_problems
                history.update_date = date.today()
                history.user = user
                history.save()
                return HttpResponse(str(solved_problems))
            except:
                return HttpResponseBadRequest('Registered already')
        else:
            return HttpResponseNotFound('please check the URL')
    else:
        return HttpResponseForbidden('GET method is not allowed for registering')


@csrf_exempt
def user(request):
    if request.method == 'GET':
        username = request.GET.get('username', None)
        users = User.objects.filter(username=username)
        if users:
            return HttpResponse(users[0].url)
        else:
            return HttpResponseNotFound('No such user')
    else:
        username = request.POST.get('username', None)
        users = User.objects.filter(username=username)
        if users:
            url = request.POST.get('url', None)
            solved_problems = parse_solved_problems(url)
            if solved_problems:
                users.update(url=url)
                return HttpResponse('Done')
            else:
                return HttpResponseNotFound('Check URL')
        else:
            return HttpResponseNotFound('No such user')


@csrf_exempt
def histroy(request):
    if request.method == 'GET':
        username = request.GET.get('username', None)
        last_histroy = get_last_history(username)
        if last_histroy:
            return HttpResponse(last_history.solved_problems)
        else:
            return HttpResponseNotFound('No such user')
    else:
        username = request.POST.get('username', None)
        diff = update_history(username)
        if diff < 0:
            return HttpResponseNotFound('No such user')
        else:
            latest_history = get_last_history(username)
            return HttpResponse(latest_history.solved_problems)
            

@csrf_exempt
def day(request):
    if request.method == 'GET':
        username = request.GET.get('username', None)
        diff = update_history(username)
        if diff == -1:
            return HttpResponseNotFound('No such user')
        elif diff == -2:
            return HttpResponse(-1 * get_last_history(username).solved_problems)
        else:
            return HttpResponse(diff)
    return HttpResponseForbidden('POST method is not allowed!')
