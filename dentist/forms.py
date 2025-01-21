from django import forms
from Sparky.models import *

class TreatmentHistoryForm(forms.ModelForm):
    class Meta:
        model = TreatmentHistory
        fields = ['appointment','description','cost','extra']

