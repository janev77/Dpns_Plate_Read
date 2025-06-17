from django.db import models

# Create your models here.
from django.db import models

class Plate(models.Model):
    plate_number = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plate_number} {self.timestamp}"
