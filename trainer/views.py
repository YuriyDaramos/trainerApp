from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def trainers_page(request):
    # Параметр "category_id"
    # /trainer => ответит "trainer_page"
    # /trainer?category=5 => ответит "category: 5"
    category_id = request.GET.get("category")
    if category_id:
        return HttpResponse(f"category: {category_id}")
    return HttpResponse("trainer_page")


def specific_trainer_page(request, trainer_id):
    return HttpResponse("specific_trainer_page")


def specific_trainer_page_service(request, trainer_id, service_id):
    # Возвращает информацию о сервисе
    return HttpResponse("specific_trainer_page_service")


def specific_trainer_page_service_booking(request, trainer_id, service_id):
    if request.method == "POST":
        return HttpResponse("specific_trainer_page_service_booking")
    return HttpResponse("Method Not Allowed", status=405)
