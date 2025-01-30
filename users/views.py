from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.utils import timezone

import trainer
from trainer.models import TrainerDescription
from booking.models import Booking
from users.models import Rating

from .forms import UserRegistrationForm, UserLoginForm, RatingAndCommentForm


def users(request):
    user_group = Group.objects.get(name="User")
    users_data = User.objects.filter(groups=user_group)

    paginator = Paginator(users_data, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "users.html", {"page_obj": page_obj})


def user_details(request, user_id):
    if request.method == "GET":
        user = User.objects.get(pk=user_id)
        trainer_description = None
        trainer_services_exists = False
        bookings = None

        if user.groups.filter(name="Trainer").exists():
            bookings = Booking.objects.filter(trainer_id=user_id).select_related("service", "service__category",
                                                                                 "service__trainer")
            trainer_description = TrainerDescription.objects.filter(trainer_id=user.id).first()
            trainer_services_exists = trainer.models.Service.objects.filter(trainer_id=user.id).exists()

        if user.groups.filter(name="User").exists():
            bookings = Booking.objects.filter(user_id=user_id).select_related("service", "service__category",
                                                                              "service__trainer")

        date_now = timezone.now()
        future_bookings = bookings.filter(datetime_start__gte=date_now).order_by("datetime_start")
        past_bookings = bookings.filter(datetime_end__lt=date_now).order_by("-datetime_end")

        has_connection = Booking.objects.filter(user_id=request.user.id, trainer_id=user.id).exists() or \
                         Booking.objects.filter(user_id=user.id, trainer_id=request.user.id).exists()

        show_my_comments = request.GET.get("show_my_comments", "false") == "true"

        if show_my_comments:
            ratings_received = Rating.objects.filter(author=user)
        else:
            ratings_received = Rating.objects.filter(recipient=user)

        existing_rating = Rating.objects.filter(author=request.user, recipient=user).first()

        initial_data = {}
        if existing_rating:
            initial_data = {"rate": existing_rating.rate,
                            "text": existing_rating.text}
        form = RatingAndCommentForm(initial=initial_data)

        return render(request, "user_page.html", {"form": form,
                                                  "user": user,
                                                  "future_bookings": future_bookings,
                                                  "past_bookings": past_bookings,
                                                  "trainer_description": trainer_description,
                                                  "trainer_services_exists": trainer_services_exists,
                                                  "ratings_received": ratings_received,
                                                  "has_connection": has_connection,
                                                  "existing_rating": existing_rating,
                                                  "show_my_comments": show_my_comments})

    if request.method == "POST":
        booking_id = request.POST.get("booking_id")
        if booking_id:
            booking = Booking.objects.get(id=booking_id)
            booking.status = False
            booking.save()

        return redirect(request.path)


def login_page(request):
    if request.method == "GET":
        form = UserLoginForm()
        return render(request, "login.html", {"form": form})

    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return render(request, "index.html", {"success": f"Log in success! Welcome, {username}."})
            else:
                form.add_error(None, "Invalid username or password.")
                return render(request, "login.html", {"form": form})


def logout_page(request):
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        return render(request, "index.html", {"success": f"Log out success! Goodbye, {username}."})
    else:
        return HttpResponseForbidden("Forbidden")


def register_page(request):
    if request.method == "GET":
        form = UserRegistrationForm()
        return render(request, "register.html", {"form": form})

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            is_trainer = form.cleaned_data.get("is_trainer")
            group_name = "Trainer" if is_trainer else "User"
            group = Group.objects.get(name=group_name)
            user.groups.add(group)

            login(request, user)
            username = user.username
            user_role = user.groups.first().name
            return render(request, "index.html",
                          {"success": f"Registrations success! Welcome, {username}. Your role: {user_role}."})
        else:
            return render(request, "register.html", {"form": form})


def add_or_update_rating(request, user_id):
    if request.method == "POST":
        rate, text = None, ""
        form = RatingAndCommentForm(request.POST)
        if form.is_valid():
            rate = form.cleaned_data["rate"]
            text = form.cleaned_data["text"]

        user = User.objects.get(pk=user_id)

        existing_rating = Rating.objects.filter(author=request.user, recipient=user).first()

        if existing_rating:
            existing_rating.rate = rate
            existing_rating.text = text
            existing_rating.save()
        else:
            Rating.objects.create(author=request.user,
                                  recipient=user,
                                  rate=rate,
                                  text=text)

        return redirect("users:user_details", user_id=user.id)
    else:
        return HttpResponseForbidden
