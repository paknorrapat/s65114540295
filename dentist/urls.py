from django.urls import path
from .views import *
urlpatterns = [
    path("dentist_home/",dentist_home,name="dentist-home"),
    path("treatment_history/",treatment_history,name="treatment-history"),
    path("add_treatmenthistory/",add_treatment_history,name="add-treatmenthistory"),
]