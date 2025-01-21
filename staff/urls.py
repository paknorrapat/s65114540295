from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path("staff_home/",staff_home,name="staff-home"),
    path("appointment/delete/<int:id>/",delete_appointment,name="appointment-delete"),
    path("appointment/add/<int:user_id>/",add_appointment,name="appointment-add"),
    path('appointment/update/<int:appointment_id>/',update_appointment, name='appointment-update'),
    
    path("dentist_manage/",dentist_manage,name="dentist-manage"),
    path("add_dentist/",add_dentist,name="add-dentist"),
    path("delete_dentist/<int:dentist_id>/",delete_dentist,name="delete-dentist"),
    path("edit_dentist/<int:dentist_id>/",edit_dentist,name="edit-dentist"),

    path("treatment_manage/",treatment_manage,name="treatment-manage"),
    path("add_treatment/",add_treatment,name="add-treatment"),
    path("delete_treatment/<int:treatment_id>/",delete_treatment,name="delete-treatment"),
    path("edit_treatment/<int:treatment_id>/",edit_treatment,name="edit-treatment"),

    path("add_extra/",add_extra,name="add-extra"),
    path("delete_extra/<int:extra_id>/",delete_extra,name="delete-extra"),
    path("edit_extra/<int:extra_id>/",edit_extra,name="edit-extra"),

    path("appointment_list/",appointment_list,name="appointment-list"),
    path("member_info/",member_info,name="member-info"),


]