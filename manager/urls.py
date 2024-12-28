from django.urls import path
from .views import *
urlpatterns = [
    path("manager_home/",manager_home,name="manager-home")
]