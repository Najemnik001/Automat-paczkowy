from django import forms
from .models import CustomUser

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.CharField()  # Dodaj inne pola w razie potrzeby

    class Meta:
        model = CustomUser
        fields = ['username', 'usersurname', 'email', 'password', 'role']
