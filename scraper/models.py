from django.db import models

# Create your models here.
class Product(models.Model):
    nom = models.CharField(max_length=250)
    prix = models.FloatField(max_length=250)
    url = models.CharField(max_length=250)

    def __init__(self, n, p,u):
        self.nom = n
        self.prix = p
        self.url = u