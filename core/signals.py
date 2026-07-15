from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Activity


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(m2m_changed, sender=Profile.followers.through)
def follower_changed(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for follower_id in pk_set:
            try:
                follower = User.objects.get(id=follower_id)
                Activity.objects.create(
                    user=instance.user,
                    actor=follower,
                    activity_type=Activity.FOLLOW,
                    text=f"{follower.username} started following you",
                )
            except User.DoesNotExist:
                pass
