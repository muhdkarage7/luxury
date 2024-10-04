from django.db import models

# Create your models here.
class contact_usImxus(models.Model):
    firstname =models.CharField(max_length=100)
    lastname =models.CharField(max_length=100)
    email =models.EmailField()
    country =models.CharField(max_length=100)
    subject =models.CharField(max_length=100)
    


    def __str__(self):
        return self.subject
