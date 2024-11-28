from django import forms
from .models import Parcel
from lockers.models import Locker
from users.models import CustomUser

class ParcelForm(forms.ModelForm):
    receiver_email = forms.EmailField(label="Receiver Email", required=True)
    sent_from_locker = forms.ModelChoiceField(
        queryset=Locker.objects.all(),
        label="Sent From Locker",
        required=True,
        empty_label="Choose Locker to Send From",
        widget=forms.Select(attrs={'placeholder': 'Search by name or location'})
    )
    sent_to_locker = forms.ModelChoiceField(
        queryset=Locker.objects.all(),
        label="Sent To Locker",
        required=True,
        empty_label="Choose Locker to Send To",
        widget=forms.Select(attrs={'placeholder': 'Search by name or location'})
    )

    class Meta:
        model = Parcel
        fields = ['name', 'package_size', 'receiver_email', 'sent_from_locker', 'sent_to_locker']

    def clean_receiver_email(self):
        email = self.cleaned_data.get('receiver_email')
        try:
            receiver = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise forms.ValidationError(f"Nie ma użytkownika z takim emailem: {email}")
        return receiver
