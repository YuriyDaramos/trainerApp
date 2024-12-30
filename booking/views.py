from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def booking_page(request, booking_id):
    return HttpResponse("booking_page")


def booking_cancel_page(request, booking_id):
    return HttpResponse("booking_cancel_page")


def booking_accept_page(request, booking_id):
    return HttpResponse("booking_accept_page")
