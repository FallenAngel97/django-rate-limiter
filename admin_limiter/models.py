from django.db import models
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.core.cache import cache
from django.dispatch import receiver
from django.db.models.signals import pre_save

User = get_user_model()

class HttpVerbs(models.TextChoices):
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PATCH = "PATCH" 
    PUT = "PUT"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class ApiLimiter(models.Model):
    speed_value = models.CharField(max_length=100, help_text='Provide the value in requests/second, such as: 5, 10, 20...')
    method = models.CharField(choices=HttpVerbs, blank=False)
    url = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.method} {self.url}"


class UserSpecificLimit(models.Model):
    affected_user = models.ForeignKey(User, on_delete=models.CASCADE)
    api_limiter = models.ForeignKey(ApiLimiter, on_delete=models.CASCADE)
    speed_value = models.CharField(max_length=100, help_text='Provide the value in requests/second, such as: 5, 10, 20...')

