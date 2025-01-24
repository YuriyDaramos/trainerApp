from datetime import timedelta, datetime, time

from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect

import trainer.models
from booking.models import Booking


# Create your views here.


def trainers(request):
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
    if request.method == "GET":
        is_trainer = request.user.is_authenticated and request.user.groups.filter(name="Trainer").exists()
        service_categories = trainer.models.Category.objects.all()
        trainer_services = trainer.models.Service.objects.filter(trainer=trainer_id)
        trainer_data = User.objects.filter(id=trainer_id).values("username", "last_name", "first_name").first()
        return render(request, "trainer.html", {"is_trainer": is_trainer,
                                                "trainer": trainer_data,
                                                "trainer_id": trainer_id,
                                                "service_categories": service_categories,
                                                "trainer_services": trainer_services})


from datetime import datetime, timedelta


def service_page(request, trainer_id):
    if request.method == "GET":
        services = trainer.models.Service.objects.filter(trainer_id=trainer_id)
        service_categories = trainer.models.Category.objects.all()
        return render(request, "service.html", {"services": services, "service_categories": service_categories})

    if request.method == "POST":
        if request.user.groups.filter(name="Trainer").exists():
            form_data = request.POST

            if "duration" in form_data:
                service_category = trainer.models.Category.objects.get(pk=form_data["category"])

                duration_minutes = int(form_data["duration"])
                duration = timedelta(minutes=duration_minutes)

                service = trainer.models.Service(
                    level=form_data["level"],
                    duration=duration,
                    price=form_data["price"],
                    category=service_category,
                    trainer=request.user,
                )
                service.save()
                return redirect(request.META.get("HTTP_REFERER", "/"))

            elif "start_datetime" in form_data and "end_datetime" in form_data:
                start_datetime = form_data.get("start_datetime")
                end_datetime = form_data.get("end_datetime")

                start_datetime_obj = datetime.fromisoformat(start_datetime)
                end_datetime_obj = datetime.fromisoformat(end_datetime)

                trainer.models.TrainerSchedule.objects.create(
                    trainer_id=trainer_id,
                    datetime_start=start_datetime_obj,
                    datetime_end=end_datetime_obj,
                )
                return redirect(request.META.get("HTTP_REFERER", "/"))

        return redirect(request.META.get("HTTP_REFERER", "/"))


def book_service(request, trainer_id, service_id, day=None):
    if request.method == "GET":
        if request.user.groups.filter(name="User").exists():
            from trainer.utils import generate_actual_calendar, booking_time_discovery
            import calendar

            service = trainer.models.Service.objects.filter(pk=service_id).first()

            date_param = request.GET.get("date")
            if date_param:
                date = datetime.strptime(date_param, "%Y-%m-%d").date()
            else:
                date = datetime.today().date()

            current_month = int(request.GET.get("month", datetime.now().month))
            current_year = int(request.GET.get("year", datetime.now().year))

            min_date = datetime.today().date()
            max_date = min_date + timedelta(days=90)
            if (current_year, current_month) > (max_date.year, max_date.month):
                current_year, current_month = max_date.year, max_date.month
            if (current_year, current_month) < (min_date.year, min_date.month):
                current_year, current_month = min_date.year, min_date.month

            calendar_rows = generate_actual_calendar(current_year, current_month, date)

            possible_times = booking_time_discovery(trainer_id, service_id, date)

            return render(request, "service.html", {
                "service": service,
                "selected_day": date,
                "calendar_rows": calendar_rows,
                "current_month_name": calendar.month_name[current_month],
                "current_year": current_year,
                "current_month": current_month,
                "possible_times": possible_times,
            })

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

            booking = Booking.objects.create(
                datetime_start=datetime_start,
                datetime_end=datetime_end,
                status=True,
                service_id=service.id,
                trainer_id=trainer_data.id,
                user_id=user.id
            )

            return redirect("trainer:book_service", trainer_id=trainer_data.id, service_id=service.id)
