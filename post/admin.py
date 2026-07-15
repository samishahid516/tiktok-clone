from django.contrib import admin
from .models import Post, Video, Image, Soundtrack, Like, Comment

admin.site.register(Post)
admin.site.register(Video)
admin.site.register(Image)
admin.site.register(Soundtrack)
admin.site.register(Like)
admin.site.register(Comment)
