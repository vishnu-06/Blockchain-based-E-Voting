from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin


class Activation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)
    totp_id = models.CharField(max_length=50, unique=True)
    public_key_ecc = models.CharField(max_length=300)
    private_key_ecc = models.CharField(max_length=300)
    aadhaar_id = models.CharField(max_length=16, default="")
    voter_id = models.CharField(max_length=16, default="")
    voting_allowed = models.CharField(max_length=3, default="")
    phone_number = models.CharField(max_length=10, default="")
    address = models.CharField(max_length=300, default="")

    def __str__(self):  
        return str(self.user)

admin.site.register(Activation)
