from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

    def __str__(self):
        return f"{self.username}"


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=256)
    basePrice = models.PositiveIntegerField()
    imageURL = models.URLField(blank=True)
    category = models.CharField(max_length=11, choices=[
        ('other', ''), ('electronics', 'Electronics'), ('furniture', 'Furniture'), ('vehicle', 'Vehicle'), ('fashion', 'Fashion')
        ], default='other')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    # watchers = models.ManyToManyField(User, related_name="watchlist", blank=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.title}"


class Bid(models.Model):
    bidValue = models.PositiveIntegerField()
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    bidObject = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder} bids {self.bidValue} on {self.bidObject}"


class Comment(models.Model):
    body = models.TextField(max_length=256, blank=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    author_name = models.TextField(max_length=150, blank=False)
    object = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author} comments on {self.object}"


class Watcher(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} is watching {self.listing}'
