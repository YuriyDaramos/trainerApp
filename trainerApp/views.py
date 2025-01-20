from django.contrib.auth.models import Group
from django.shortcuts import render, redirect


def index(request):
    return render(request, "index.html")


def hot_change_group(request):
    if request.user.groups.filter(name="User").exists():
        group = Group.objects.get(name="Trainer")
    else:
        group = Group.objects.get(name="User")

    request.user.groups.clear()
    request.user.groups.add(group)
    request.user.save()

    return redirect(request.META.get("HTTP_REFERER", "/"))
