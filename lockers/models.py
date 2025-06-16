from django.db import models

class Locker(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)

    def __str__(self):
        return f"Locker: {self.name} at {self.location}"

    def get_free_locks(self):
        return self.locks.filter(is_free=True)

class Lock(models.Model):
    SIZE_CHOICES = [
        ('small', 'Small'),
        ('large', 'Large'),
    ]

    locker = models.ForeignKey(Locker, on_delete=models.CASCADE, related_name="locks")
    size = models.CharField(max_length=5, choices=SIZE_CHOICES)
    is_free = models.BooleanField(default=True)

    def __str__(self):
        return f"Lock in {self.locker.name} ({self.size}) - {'Free' if self.is_free else 'Occupied'}"
