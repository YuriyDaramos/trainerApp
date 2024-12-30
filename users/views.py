from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def user_page(request):
    return HttpResponse("user_page")


def specific_user_page(request, user_id):
    return HttpResponse("specific_user_page")


def login_page(request):
    return HttpResponse("login_page")


def logout_page(request):
    return HttpResponse("logout_page")


def register_page(request):
    return HttpResponse("register_page")
