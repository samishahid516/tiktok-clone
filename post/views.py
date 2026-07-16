import json
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.conf import settings
from .models import Post, Video, Image, Soundtrack, Like, Comment, CommentLike, Bookmark
from .forms import PostForm, CommentForm
from core.models import Activity


@login_required
def upload(request):
    sound_tracks_dir = os.path.join(settings.MEDIA_ROOT, 'sound_tracks')
    sound_tracks = []
    if os.path.exists(sound_tracks_dir):
        sound_tracks = [f for f in os.listdir(sound_tracks_dir) if f.endswith(('.mp3', '.wav', '.ogg', '.m4a', '.flac'))]

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()

            media_file = request.FILES.get('media')
            if media_file:
                content_type = media_file.content_type or ''
                if content_type.startswith('video/'):
                    v = Video.objects.create(file=media_file)
                    post.video = v
                else:
                    img = Image.objects.create(file=media_file)
                    post.image = img
                post.save()

            soundtrack_name = request.POST.get('soundtrack', '')
            if soundtrack_name:
                s = Soundtrack.objects.create(title=soundtrack_name)
                post.soundtrack = s
                post.save()

            return redirect('home')

    return render(request, 'post/upload.html', {'sound_tracks': sound_tracks, 'sound_tracks_json': json.dumps(sound_tracks)})


@login_required
def post_detail(request, post_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    post = get_object_or_404(Post.objects.select_related('video', 'image', 'soundtrack').prefetch_related('comment_set__user', 'comment_set__replies__user', 'like_set__user'), id=post_id)
    likers = post.like_set.select_related('user').all()
    next_post = Post.objects.filter(id__gt=post_id).order_by('id').first()
    prev_post = Post.objects.filter(id__lt=post_id).order_by('-id').first()
    return render(request, 'post/detail.html', {
        'post': post,
        'likers': likers,
        'next_post_id': next_post.id if next_post else None,
        'prev_post_id': prev_post.id if prev_post else None,
    })


@login_required
def update_post(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    post = get_object_or_404(Post, id=post_id, user=request.user)
    form = PostForm(request.POST, instance=post)
    if form.is_valid():
        form.save()
        soundtrack_name = request.POST.get('soundtrack', '')
        if soundtrack_name:
            if post.soundtrack:
                post.soundtrack.title = soundtrack_name
                post.soundtrack.save()
            else:
                s = Soundtrack.objects.create(title=soundtrack_name)
                post.soundtrack = s
                post.save()

        video_file = request.FILES.get('video')
        if video_file:
            if post.video:
                post.video.file = video_file
                post.video.save()
            else:
                v = Video.objects.create(file=video_file)
                post.video = v
                post.save()

        image_file = request.FILES.get('image')
        if image_file:
            if post.image:
                post.image.file = image_file
                post.image.save()
            else:
                img = Image.objects.create(file=image_file)
                post.image = img
                post.save()

        return redirect('post_detail', post_id=post.id)
    return redirect('post_detail', post_id=post.id)


@login_required
def delete_post(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    post = get_object_or_404(Post, id=post_id, user=request.user)
    post.delete()
    return redirect('home')


@login_required
def like_post(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'total_likes': post.like_set.count()})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'GET':
        comments = post.comment_set.filter(parent=None).select_related('user').prefetch_related('replies__user', 'likes').order_by('-created_at')
        data = []
        for c in comments:
            replies_data = []
            for r in c.replies.select_related('user').prefetch_related('likes').order_by('created_at'):
                replies_data.append({
                    'id': r.id,
                    'username': r.user.username,
                    'text': r.text,
                    'created_at': r.created_at.isoformat(),
                    'likes': r.likes.count(),
                    'liked': r.likes.filter(user=request.user).exists(),
                })
            data.append({
                'id': c.id,
                'username': c.user.username,
                'text': c.text,
                'created_at': c.created_at.isoformat(),
                'likes': c.likes.count(),
                'liked': c.likes.filter(user=request.user).exists(),
                'replies': replies_data,
                'reply_count': c.replies.count(),
            })
        return JsonResponse({'comments': data})

    elif request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent_id = parent_id
            comment.save()
            return JsonResponse({
                'success': True,
                'id': comment.id,
                'username': comment.user.username,
                'text': comment.text,
                'created_at': comment.created_at.isoformat(),
                'likes': 0,
                'liked': False,
                'reply_count': 0,
                'replies': [],
                'parent_id': comment.parent_id,
            })
        return JsonResponse({'error': 'Invalid form'}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def like_comment(request, comment_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    comment = get_object_or_404(Comment, id=comment_id)
    like, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'total_likes': comment.likes.count()})


@login_required
def toggle_bookmark(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    post = get_object_or_404(Post, id=post_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)
    if not created:
        bookmark.delete()
        bookmarked = False
    else:
        bookmarked = True
    return JsonResponse({'bookmarked': bookmarked})


@login_required
def delete_comment(request, comment_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    comment.delete()
    return JsonResponse({'success': True})


@login_required
def conversations(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    comments = Comment.objects.filter(post__user=request.user).exclude(user=request.user).select_related('user', 'post').prefetch_related('likes').order_by('-created_at')
    seen = {}
    for c in comments:
        if c.user.id not in seen:
            seen[c.user.id] = {
                'user_id': c.user.id,
                'username': c.user.username,
                'text': c.text,
                'post_id': c.post.id,
                'comment_id': c.id,
                'time': c.created_at.isoformat(),
                'liked': c.likes.filter(user=request.user).exists(),
            }
    return JsonResponse({'conversations': list(seen.values())})


@login_required
def activities(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    activity_type = request.GET.get('type', 'all')
    qs = Activity.objects.filter(user=request.user)
    if activity_type != 'all':
        qs = qs.filter(activity_type=activity_type)
    data = []
    for a in qs[:50]:
        data.append({
            'id': a.id,
            'type': a.activity_type,
            'actor': a.actor.username,
            'actor_id': a.actor.id,
            'text': a.text,
            'post_id': a.post.id if a.post else None,
            'comment_id': a.comment.id if a.comment else None,
            'time': a.created_at.isoformat(),
        })
    return JsonResponse({'activities': data})
