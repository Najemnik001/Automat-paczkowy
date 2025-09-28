from django import forms
from .models import Parcel
from lockers.models import Locker
from users.models import CustomUser

class ParcelForm(forms.ModelForm):
    receiver_email = forms.EmailField(label="Email odbiorcy", required=True)
    sent_from_machine = forms.ModelChoiceField(
        queryset=Locker.objects.all(),
        label="Wyślij z paczkomatu",
        required=True,
        empty_label="Wybierz paczkomat nadawczy",
        widget=forms.Select(attrs={'placeholder': 'Szukaj po nazwie lub lokalizacji'})
    )
    sent_to_machine = forms.ModelChoiceField(
        queryset=Locker.objects.all(),
        label="Dostarcz do paczkomatu",
        required=True,
        empty_label="Wybierz paczkomat docelowy",
        widget=forms.Select(attrs={'placeholder': 'Szukaj po nazwie lub lokalizacji'})
    )

    class Meta:
        model = Parcel
        fields = ['name', 'package_size', 'sent_from_machine', 'sent_to_machine', 'receiver_email']

    def clean_receiver_email(self):
        email = self.cleaned_data.get('receiver_email')
        try:
            receiver = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise forms.ValidationError(f"Nie znaleziono użytkownika o adresie: {email}")
        return receiver
