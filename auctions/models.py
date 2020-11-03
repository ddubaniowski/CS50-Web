from django.contrib.auth.models import AbstractUser
from django.db import models

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    image = models.ImageField()
    current_bid = models.FloatField()
    watch = models.BooleanField(default=False)
    category = models.CharField(max_length=64, default="none")
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=64, default="none")
    closed = models.BooleanField(default=False)
    winner_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Item {self.id}: {self.title}, Price: {self.current_bid}"

class User(AbstractUser):
    watchlist = models.ManyToManyField(Listing, related_name="users")
    pass

class Bid(models.Model):
    bid = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Listing, on_delete=models.CASCADE)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    item = models.ForeignKey(Listing, on_delete=models.CASCADE)
