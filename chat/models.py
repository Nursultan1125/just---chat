from django.db import models


# Create your models here.

class ConnectionPerson(models.Model):
    count_connection = models.IntegerField(default=0)

