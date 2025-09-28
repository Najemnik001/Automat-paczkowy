from .models import CustomUser
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Hasło",
        widget=forms.PasswordInput(attrs={'placeholder': 'Wpisz hasło'}),
        error_messages={
            'required': 'To pole jest wymagane.',
        }
    )
    password2 = forms.CharField(
        label="Powtórz hasło",
        widget=forms.PasswordInput(attrs={'placeholder': 'Powtórz hasło'}),
        error_messages={
            'required': 'To pole jest wymagane.',
        }
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'usersurname', 'email']
        labels = {
            'username': 'Imię',
            'usersurname': 'Nazwisko',
            'email': 'Adres e-mail',
        }
        error_messages = {
            'username': {
                'required': 'To pole jest wymagane.',
                'max_length': 'Maksymalna długość to 150 znaków.',
                'invalid': 'Imię może zawierać tylko litery, cyfry oraz znaki @/./+/-/_'
            },
            'usersurname': {
                'required': 'Nazwisko jest wymagane.'
            },
            'email': {
                'required': 'To pole jest wymagane.',
                'invalid': 'Wprowadź poprawny adres e-mail.',
                'unique': 'Użytkownik z tym adresem e-mail już istnieje.'
            }
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Hasła nie są takie same!")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label=("Adres e-mail"),
        widget=forms.EmailInput(attrs={"autofocus": True})
    )

    error_messages = {
        "invalid_login": "Wprowadź poprawny adres e-mail i hasło.",
        "inactive": "To konto jest nieaktywne.",
    }