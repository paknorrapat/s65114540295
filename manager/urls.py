from django.urls import path
from .views import *
urlpatterns = [
    path("dashboard/",dashboard,name="dashboard"),
    path("dashboard2/",second_dashboard,name="dashboard2"),
    path("user_list/",user_list,name="user-list"),
    path("dentist_list/",dentist_list,name="dentist-list"),
    path("staff_list/",staff_list,name="staff-list"),
    path('update_role/', update_role, name='update_role'),
    path("delete_user/<int:user_id>/",delete_user,name="delete-user"),
]