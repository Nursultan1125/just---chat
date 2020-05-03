from django.db import models
from django.contrib.auth import get_user_model


# Create your models here.
User = get_user_model()

class ConnectionPerson(models.Model):
    count_connection = models.IntegerField(default=0)


class Message(models.Model):
    author = models.ForeignKey(User, related_name="author_message", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.username

    def last_10_message(self):
        return Message.objects.order_by('-timestamp').all()[:10]

