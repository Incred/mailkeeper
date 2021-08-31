from django import forms
from django.contrib.auth.models import BaseUserManager


class SendEmailForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'E-mail address'}),
        label=''
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        return BaseUserManager.normalize_email(email).lower()
