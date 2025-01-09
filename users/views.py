from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render


def user_page(request):
    return HttpResponse("user_page")


def specific_user_page(request, user_id):
    return HttpResponse("specific_user_page")


def login_page(request):
    if request.method == "GET":
        return render(request, "login.html")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:

            # --- for testing only ---
            delete_user = request.POST.get("delete_user")
            if delete_user:
                user = User.objects.get(username=username)
                user.delete()
                return render(request, "login.html", {"error": f"User '{username}' deleted"})
            # --- for testing only ---

            login(request, user)
            return HttpResponse("Login success!")
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})


def logout_page(request):
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        return HttpResponse(f"Logout success! Goodbye, {username}.")
    else:
        return HttpResponse("Log in first")


def register_page(request):
    if request.method == "GET":
        return render(request, "register.html")

    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
        user.save()
        return HttpResponse(f"Registration success! Hello, {username}!")
