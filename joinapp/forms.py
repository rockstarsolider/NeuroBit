from django import forms
from .models import Application

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['full_name', 'phone', 'location', 'age', 'sopfile']
        widgets = {
            'full_name': forms.TextInput(attrs={'id':'fullName'}),
            'phone':     forms.TextInput(attrs={'id':'phone'}),
            'location':  forms.TextInput(attrs={'id':'location'}),
            'age':       forms.NumberInput(attrs={'id':'age', 'min':10,'max':99}),
        }
