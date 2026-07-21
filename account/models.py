
# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    TYPE1 = "type1"
    TYPE2 = "type2"
    TYPE3 = "type3"

    ROLE_CHOICES = [
        (TYPE1, "Type 1"),
        (TYPE2, "Type 2"),
        (TYPE3, "Type 3"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=TYPE3
    )

    def __str__(self):
        return self.username