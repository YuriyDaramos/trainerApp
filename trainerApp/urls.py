"""
URL configuration for trainerApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

import trainer.views
import users.views
from trainerApp import views

urlpatterns = [
    path("", views.index, name="index"),
    path("admin/", admin.site.urls),
    path("register/", users.views.register_page, name="user_register"),
    path("login/", users.views.login_page, name="user_login"),
    path("logout/", users.views.logout_page, name="user_logout"),
    path("user/", include(("users.urls", "users"), namespace="users")),
    path("booking/", include(("booking.urls", "booking"), namespace="booking")),
    path("trainer/", include(("trainer.urls", "trainer"), namespace="trainer")),
]
