from django import forms
from lockers.models import Locker

class LockerForm(forms.ModelForm):
    small_boxes = forms.IntegerField(label="Ilość małych skrytek", min_value=0, required=True)
    large_boxes = forms.IntegerField(label="Ilość dużych skrytek", min_value=0, required=True)

    class Meta:
        model = Locker
        fields = ['name', 'location']

        labels = {
            'name': 'Nazwa skrytki',
            'location': 'Lokalizacja',
        }

class LockerEditForm(forms.ModelForm):
    small_boxes = forms.IntegerField(label="Ilość małych skrytek", min_value=0, required=True)
    large_boxes = forms.IntegerField(label="Ilość dużych skrytek", min_value=0, required=True)

    class Meta:
        model = Locker
        fields = ['name', 'location']

        labels = {
            'name': 'Nazwa skrytki',
            'location': 'Lokalizacja',
        }

    def __init__(self, *args, **kwargs):
        locker = kwargs.pop('locker', None)
        super().__init__(*args, **kwargs)
        if locker:
            self.fields['name'].initial = locker.name
            self.fields['location'].initial = locker.location
            self.fields['small_boxes'].initial = locker.locks.filter(size='small').count()
            self.fields['large_boxes'].initial = locker.locks.filter(size='large').count()
