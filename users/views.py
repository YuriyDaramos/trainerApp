from collections import defaultdict

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.timezone import now

import trainer
from trainer.models import TrainerDescription
from booking.models import Booking


def users(request):
    user_group = Group.objects.get(name="User")
    users_data = User.objects.filter(groups=user_group)

    paginator = Paginator(users_data, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "users.html", {"page_obj": page_obj})


def user_details(request, user_id):
    user = User.objects.get(pk=user_id)
    if user.groups.filter(name="Trainer").exists():
        bookings = Booking.objects.filter(trainer_id=user_id).select_related("service", "service__category",
                                                                             "service__trainer")
    else:
        bookings = Booking.objects.filter(user_id=user_id).select_related("service", "service__category",
                                                                          "service__trainer")

    now = timezone.now()
    future_bookings = bookings.filter(datetime_start__gte=now).order_by("datetime_start")
    past_bookings = bookings.filter(datetime_end__lt=now).order_by("-datetime_end")

    trainer_description = None
    trainer_services_exists = False
    if user.groups.filter(name="Trainer").exists():
        trainer_description = TrainerDescription.objects.filter(trainer_id=user.id).first()
        trainer_services_exists = trainer.models.Service.objects.filter(trainer_id=user.id).exists()

    if request.method == "POST":
        booking_id = request.POST.get("booking_id")
        if booking_id:
            booking = Booking.objects.get(id=booking_id)
            booking.status = False
            booking.save()
        return redirect(request.path)

    return render(request, "user_page.html", {"user": user,
                                              "future_bookings": future_bookings,
                                              "past_bookings": past_bookings,
                                              "trainer_description": trainer_description,
                                              "trainer_services_exists": trainer_services_exists})


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
                return render(request, "index.html", {"warning": f"User '{username}' deleted"})
            # --- for testing only ---

            login(request, user)
            return render(request, "index.html", {"success": f"Log in success! Welcome, {username}."})
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})


def logout_page(request):
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        return render(request, "index.html", {"success": f"Log out success! Goodbye, {username}."})
    else:
        return render(request, "index.html", {"warning": f"Log in first."})


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

        is_trainer = request.POST.get("is_trainer") == 'on'
        group_name = "Trainer" if is_trainer else "User"
        group = Group.objects.get(name=group_name)
        user.groups.add(group)

        user.save()

        login(request, user)
        user_role = user.groups.first().name
        return render(request, "index.html",
                      {"success": f"Registrations success! Welcome, {username}. Your role: {user_role}."})
