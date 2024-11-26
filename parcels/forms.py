from django import forms
from django.contrib.auth import get_user_model
from .models import Parcel

User = get_user_model()

class ParcelForm(forms.ModelForm):
    receiver_email = forms.EmailField(label="Receiver Email", required=True)

    class Meta:
        model = Parcel
        fields = ['name', 'package_size', 'receiver_email', 'sent_to_machine']

    def clean_receiver_email(self):
        email = self.cleaned_data.get('receiver_email')
        try:
            receiver = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError(f"Nie ma użytwkownika z takim emailem: {email}")
        return receiver
