from django.urls import path
from .views import *
urlpatterns = [
    path("dentist_home/",dentist_home,name="dentist-home"),
    path("treatment_history/",treatment_history,name="treatment-history"),
    path("add_treatmenthistory/<int:apt_id>/",add_treatment_history,name="add-treatmenthistory"),
    path('t_history_all/',t_history_all,name='t-history-all'),
    path('update_t_history/<int:treatment_history_id>/',update_treatment_history,name='update-t-history'),
]