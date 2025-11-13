from django import forms

from .models import CustomUser


class LoginForm(forms.Form):
    phone_number = forms.CharField(
        max_length=11,
        label='',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none',
            'placeholder': 'Phone Number',
        })
    )