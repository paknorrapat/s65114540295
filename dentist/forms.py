from django import forms
from Sparky.models import *

class TreatementHistoryForm(forms.ModelForm):
    class Meta:
        model = TreatmentHistory
        fields = ['appointment','description','cost']

