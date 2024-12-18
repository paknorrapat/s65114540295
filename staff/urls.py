from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path("staff_home/",staff_home,name="staff-home"),
    path("appointment/delete/<int:id>/",delete_appointment,name="appointment-delete"),
    path("appointment/add/",add_appointment,name="appointment-add"),
    path("appointment/edit/<int:appointment_id>/",edit_appointment,name="appointment-edit"),
    path("appointment/add_braces/",add_braces_appointment,name="appointment-add-braces"),

    path("dentist_manage/",dentist_manage,name="dentist-manage"),
    path("add_dentist/",add_dentist,name="add-dentist"),
    path("delete_dentist/<int:dentist_id>/",delete_dentist,name="delete-dentist"),
    path("edit_dentist/<int:dentist_id>/",edit_dentist,name="edit-dentist"),

    path("treatment_manage/",treatment_manage,name="treatment-manage"),
    path("add_treatment/",add_treatment,name="add-treatment"),
    path("delete_treatment/<int:treatment_id>/",delete_treatment,name="delete-treatment"),
    path("edit_treatment/<int:treatment_id>/",edit_treatment,name="edit-treatment"),

    path("appointment_list/",appointment_list,name="appointment-list"),


]