from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.utils import timezone

import trainer.models
from booking.models import Booking

from datetime import datetime, timedelta

# Create your views here.
from trainer.forms import AddTrainerService, SetWorkingHours, EditTrainerService, SetDescription


def trainers(request):
    """ Отображение всех тренеров по категориям. """
    selected_category = request.GET.get("category", "all")

    trainer_group = Group.objects.get(name="Trainer")
    trainers = User.objects.filter(groups=trainer_group)

    if selected_category != "all":
        trainers = trainers.filter(service__category__id=selected_category).distinct()

    categories = trainer.models.Category.objects.all()

    paginator = Paginator(trainers, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "trainers.html", {"page_obj": page_obj,
                                             "categories": categories,
                                             "selected_category": selected_category})


def trainer_detail(request, trainer_id):
    """ Страница тренера: настройки сервисов, рабочего времени. """
    is_trainer = request.user.is_authenticated and request.user.groups.filter(name="Trainer").exists()
    service_categories = trainer.models.Category.objects.all()
    trainer_services = trainer.models.Service.objects.filter(trainer=trainer_id)
    trainer_data = User.objects.filter(id=trainer_id).first()
    form_add_service = AddTrainerService()
    form_set_working_hours = SetWorkingHours()
    form_set_description = SetDescription()

    if request.method == "POST":
        pass

    return render(request, "trainer.html", {"form_add_service": form_add_service,
                                            "form_set_working_hours": form_set_working_hours,
                                            "form_set_description": form_set_description,
                                            "is_trainer": is_trainer,
                                            "trainer": trainer_data,
                                            "trainer_id": trainer_id,
                                            "service_categories": service_categories,
                                            "trainer_services": trainer_services})


def book_service(request, trainer_id, service_id, day=None):
    if request.method == "GET":
        if request.user.groups.filter(name="User").exists():
            from trainer.utils import generate_actual_calendar, booking_time_discovery
            service = trainer.models.Service.objects.filter(pk=service_id).first()

            date_param = request.GET.get("date")
            if date_param:
                date = datetime.strptime(date_param, "%Y-%m-%d").date()
            else:
                now = datetime.now()
                date = now.date()

            current_month = int(request.GET.get("month", timezone.now().month))
            current_year = int(request.GET.get("year", timezone.now().year))

            min_date = timezone.now().date()
            max_date = min_date + timedelta(days=90)
            if (current_year, current_month) > (max_date.year, max_date.month):
                current_year, current_month = max_date.year, max_date.month
            if (current_year, current_month) < (min_date.year, min_date.month):
                current_year, current_month = min_date.year, min_date.month

            # Расчёт следующих месяцев и годов
            next_month = current_month + 1 if current_month < 12 else 1
            next_year = current_year if current_month < 12 else current_year + 1

            next_next_month = next_month + 1 if next_month < 12 else 1
            next_next_year = next_year if next_month < 12 else next_year + 1

            # Генерация календарей
            calendar_rows = generate_actual_calendar(current_year, current_month, date)
            next_calendar_rows = generate_actual_calendar(next_year, next_month, date)
            next_next_calendar_rows = generate_actual_calendar(next_next_year, next_next_month, date)

            possible_times = booking_time_discovery(trainer_id, service_id, date)
            if not day:
                now = datetime.now()
                day = now.date()

            return render(request, "service.html", {"service": service,
                                                    "calendar_rows": calendar_rows,
                                                    "next_calendar_rows": next_calendar_rows,
                                                    "next_next_calendar_rows": next_next_calendar_rows,
                                                    "current_month": current_month,
                                                    "current_year": current_year,
                                                    "next_month": next_month,
                                                    "next_year": next_year,
                                                    "next_next_month": next_next_month,
                                                    "next_next_year": next_next_year,
                                                    "possible_times": possible_times,
                                                    "selected_day": date})

    if request.method == "POST":
        if request.user.groups.filter(name="User").exists():
            date = request.POST.get("date")
            booking_time = request.POST.get("booking_time")

            if booking_time:
                time_start, time_end = booking_time.split("-")
            else:
                time_start = time_end = None

            user = request.user
            trainer_data = User.objects.get(id=trainer_id)
            service = trainer.models.Service.objects.get(id=service_id)

            datetime_start = datetime.combine(datetime.strptime(date, "%Y-%m-%d").date(),
                                              datetime.strptime(time_start, "%H:%M").time())
            datetime_end = datetime.combine(datetime.strptime(date, "%Y-%m-%d").date(),
                                            datetime.strptime(time_end, "%H:%M").time())

            booking = Booking.objects.create(datetime_start=datetime_start,
                                             datetime_end=datetime_end,
                                             status=True,
                                             service_id=service.id,
                                             trainer_id=trainer_data.id,
                                             user_id=user.id)

            return redirect("trainer:book_service", trainer_id=trainer_data.id, service_id=service.id)
    return HttpResponseForbidden("Forbidden")


def add_trainer_service(request, trainer_id):
    if request.method == "POST":
        if request.user.groups.filter(name="Trainer").exists():
            form = AddTrainerService(request.POST)
            if form.is_valid():
                duration = 60 * form.cleaned_data["duration"]
                service = trainer.models.Service(level=form.cleaned_data["level"],
                                                 duration=duration,
                                                 price=form.cleaned_data["price"],
                                                 category=form.cleaned_data["category"],
                                                 trainer=request.user)
                service.save()

                return redirect("trainer:trainer_detail", trainer_id=trainer_id)
        else:
            return HttpResponseForbidden


def edit_trainer_service(request, trainer_id, service_id):
    if request.method == "GET":
        if request.user.groups.filter(name="Trainer").exists():
            service = trainer.models.Service.objects.get(id=service_id, trainer=request.user)
            form = EditTrainerService(instance=service)

            return render(request, "edit_services.html", {"form": form,
                                                          "trainer_id": trainer_id,
                                                          "service_id": service_id})
    if request.method == "POST":
        if request.user.groups.filter(name="Trainer").exists():
            service = trainer.models.Service.objects.get(id=service_id,
                                                         trainer=request.user)
            form = EditTrainerService(request.POST, instance=service)
            if form.is_valid():
                form.save()
                if form.cleaned_data.get("delete"):
                    service.delete()
                return redirect("trainer:trainer_detail", trainer_id=trainer_id)

    return HttpResponseForbidden("Forbidden")


def set_working_hours(request, trainer_id):
    if request.method == "POST":
        if request.user.groups.filter(name="Trainer").exists():
            form = SetWorkingHours(request.POST)
            if form.is_valid():
                schedule = trainer.models.TrainerSchedule(datetime_start=form.cleaned_data["datetime_start"],
                                                          datetime_end=form.cleaned_data["datetime_end"],
                                                          trainer=request.user)
                schedule.save()
                return redirect("trainer:trainer_detail", trainer_id=trainer_id)
        else:
            return HttpResponseForbidden


def set_trainer_description(request, trainer_id):
    if request.method == "POST":
        if request.user.groups.filter(name="Trainer").exists():
            form = SetDescription(request.POST)
            if form.is_valid():
                description, created = trainer.models.TrainerDescription.objects.get_or_create(
                    trainer=request.user,
                    defaults={"text": form.cleaned_data["text"]})

                if not created:
                    description.text = form.cleaned_data["text"]
                    description.save()

                return redirect("trainer:trainer_detail", trainer_id=trainer_id)

    return HttpResponseForbidden("Forbidden")
