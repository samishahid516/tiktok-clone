import os
import re
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Post, Video, Image, Like, Comment
from core.models import Activity


@receiver(post_save, sender=Post)
def post_created(sender, instance, created, **kwargs):
    if created:
        print(f"[Post Signal] New post created by {instance.user.username}")


@receiver(pre_delete, sender=Post)
def post_cleanup(sender, instance, **kwargs):
    if instance.video and instance.video.file and os.path.isfile(instance.video.file.path):
        os.remove(instance.video.file.path)
    if instance.image and instance.image.file and os.path.isfile(instance.image.file.path):
        os.remove(instance.image.file.path)
    if instance.soundtrack and instance.soundtrack.file and instance.soundtrack.file.path and os.path.isfile(instance.soundtrack.file.path):
        os.remove(instance.soundtrack.file.path)


@receiver(pre_delete, sender=Video)
def video_cleanup(sender, instance, **kwargs):
    if instance.file and os.path.isfile(instance.file.path):
        os.remove(instance.file.path)


@receiver(pre_delete, sender=Image)
def image_cleanup(sender, instance, **kwargs):
    if instance.file and os.path.isfile(instance.file.path):
        os.remove(instance.file.path)


@receiver(post_save, sender=Like)
def like_created(sender, instance, created, **kwargs):
    if created:
        print(f"[Like Signal] {instance.user.username} liked post {instance.post.id}")
        if instance.post.user != instance.user:
            Activity.objects.create(
                user=instance.post.user,
                actor=instance.user,
                activity_type=Activity.LIKE,
                post=instance.post,
                text=f"{instance.user.username} liked your video",
            )


@receiver(post_save, sender=Comment)
def comment_created(sender, instance, created, **kwargs):
    if created:
        print(f"[Comment Signal] {instance.user.username} commented on post {instance.post.id}")
        if instance.post.user != instance.user:
            Activity.objects.create(
                user=instance.post.user,
                actor=instance.user,
                activity_type=Activity.COMMENT,
                post=instance.post,
                comment=instance,
                text=f"{instance.user.username} commented: {instance.text[:50]}",
            )
        mentions = re.findall(r'@(\w+)', instance.text)
        for username in mentions:
            try:
                mentioned_user = User.objects.get(username=username)
                if mentioned_user != instance.user:
                    Activity.objects.create(
                        user=mentioned_user,
                        actor=instance.user,
                        activity_type=Activity.MENTION,
                        post=instance.post,
                        text=f"{instance.user.username} mentioned you in a comment",
                    )
            except User.DoesNotExist:
                pass
