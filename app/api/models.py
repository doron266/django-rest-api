import uuid
from django.db import models


class User(models.Model):
    """
    User model for the API. This model is stored in the database.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200, blank=False, null=False)
    email = models.EmailField(max_length=200, unique=True, blank=False, null=False)
    age = models.IntegerField(null=False, blank=False)

    class Meta:
        app_label = "api"


class Order(models.Model):
    """Order model for storing product orders in the database."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.CharField(max_length=200, blank=False, null=False)
    phone_number = models.CharField(max_length=30, blank=False, null=False)
    email = models.EmailField(max_length=200, blank=False, null=False)
    products = models.JSONField(default=list)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        app_label = "api"
