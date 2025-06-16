from django import forms
from .models import CustomUser

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.CharField()

    class Meta:
        model = CustomUser
        fields = ['username', 'usersurname', 'email', 'password', 'role']
