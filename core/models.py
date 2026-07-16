from django.db import models
from django.contrib.auth.models import User
import random

class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(random.randint(100000, 999999))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='user/profile_pictures/', blank=True, null=True)
    followers = models.ManyToManyField(User, related_name='following', blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Activity(models.Model):
    LIKE = 'like'
    COMMENT = 'comment'
    FOLLOW = 'follow'
    MENTION = 'mention'
    ACTIVITY_TYPES = [
        (LIKE, 'Like'),
        (COMMENT, 'Comment'),
        (FOLLOW, 'Follow'),
        (MENTION, 'Mention'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities_actor')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    post = models.ForeignKey('post.Post', on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.ForeignKey('post.Comment', on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.actor.username} {self.activity_type}"