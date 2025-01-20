from datetime import timedelta

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
import trainer.models


def trainers_page(request):
    # Параметр "category_id"
    # /trainer => ответит "trainer_page"
    # /trainer?category=5 => ответит "category: 5"
    category_id = request.GET.get("category")
    if category_id:
        return HttpResponse(f"category: {category_id}")
    return HttpResponse("trainers_page")


def specific_trainer_page(request, trainer_id):
    if request.method == "GET":
        service_categories = trainer.models.Category.objects.all()
        trainer_services = trainer.models.Service.objects.filter(trainer=request.user)
        return render(request, "trainer.html", {"service_categories": service_categories,
                                                "trainer_services": trainer_services})


def specific_trainer_page_service(request, trainer_id, service_id):
    return HttpResponse("specific_trainer_page_service")


def service_page(request):
    # Возвращает информацию о сервисе
    if request.method == "POST":
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
    return HttpResponse("service_page")


def specific_trainer_page_service_booking(request, trainer_id, service_id):
    if request.method == "POST":
        return HttpResponse("specific_trainer_page_service_booking")
    return HttpResponse("Method Not Allowed", status=405)
