from datetime import timedelta

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect

import trainer.models


# Create your views here.


def trainers(request):
    # Параметр "category_id"
    # /trainer => ответит "trainer_page"
    # /trainer?category=5 => ответит "category: 5"
    category_id = request.GET.get("category")
    if category_id:
        return HttpResponse(f"category: {category_id}")
    return HttpResponse("trainers_page")


def trainer_detail(request, trainer_id):
    if request.user.groups.filter(name="Trainer").exists():
        if request.method == "GET":
            service_categories = trainer.models.Category.objects.all()
            trainer_services = trainer.models.Service.objects.filter(trainer=request.user)
            return render(request, "trainer.html", {"trainer_id": trainer_id,
                                                    "service_categories": service_categories,
                                                    "trainer_services": trainer_services})
    else:
        trainer_model = User.objects.get(pk=trainer_id)
        trainer_data = trainer.models.TrainerDescription.objects.filter(trainer=trainer_model)
        trainer_schedule = trainer.models.TrainerSchedule.objects.filter(trainer=trainer_model)
        return render(request, "account.html", {"trainer_data": trainer_data, "trainer_schedule": trainer_schedule})


def service_page(request, trainer_id):
    if request.method == "GET":
        services = trainer.Service.objects.all()
        return render(request, "services.html", {"services": services})

    if request.method == "POST":
        if request.user.groups.filter(name="Trainer").exists():
            form_data = request.POST
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
        else:
            return redirect(request.META.get("HTTP_REFERER", "/"))


def book_service(request, trainer_id, service_id):
    if request.method == "POST":
        return HttpResponse("specific_trainer_page_service_booking")
    return HttpResponseForbidden()
