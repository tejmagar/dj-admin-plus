from django import forms


class AdminLoginForm(forms.Form):
    login = forms.CharField()
    password = forms.CharField()
