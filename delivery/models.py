from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


# Create your models here.
class users(models.Model):
    username = models.CharField(max_length=150)
    fullname = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=150)
    security_question_1 = models.CharField(max_length=500, null=True)
    answer_1 = models.CharField(max_length=500, null=True)
    security_question_2 = models.CharField(max_length=500, null=True)
    answer_2 = models.CharField(max_length=500, null=True)
    user_type = models.CharField(max_length=100)
    register_date = models.DateTimeField()

class orders(models.Model):
    trackingid = models.CharField(max_length=100)
    username = models.CharField(max_length=150)
    orderdate = models.DateField()
    destination_address = models.CharField(max_length=500)
    source_address = models.CharField(max_length=500)
    delivery_service = models.CharField(max_length=200)
    package_weight = models.CharField(max_length=50)


class deliveries(models.Model):
    trackingid = models.CharField(max_length=100)
    driver = models.CharField(max_length=150)
    status = models.CharField(max_length=50)
    current_city = models.CharField(max_length=100, null=True)
    current_state = models.CharField(max_length=100, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

class services(models.Model):
    name = models.CharField(max_length=200)
    package_size = models.CharField(max_length =50)
    price = models.FloatField()


