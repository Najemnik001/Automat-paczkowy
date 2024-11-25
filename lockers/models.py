from django.db import models

from django.db import models

class Locker(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    number_of_boxes = models.PositiveIntegerField()
