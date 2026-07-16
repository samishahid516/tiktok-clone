import json
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Q
from .models import EmailVerification, Profile, Activity
from post.models import Post, Like, Bookmark

def _send_code(email, code, user):
    subject = 'Your TikTok verification code'
    html_message = render_to_string('emails/verify_email.html', {
        'user': user,
        'code': code,
    })
    plain_message = strip_tags(html_message)
    send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [email], html_message=html_message)

def index(request):
    return render(request, 'user/index.html')

def home(request):
    posts = Post.objects.select_related('video', 'image').prefetch_related('like_set', 'comment_set', 'user').all().order_by('-created_at')

    posts_data = []
    for post in posts:
        video = post.video
        image = post.image
        liked = False
        bookmarked = False
        if request.user.is_authenticated:
            liked = post.like_set.filter(user=request.user).exists()
            bookmarked = post.bookmark_set.filter(user=request.user).exists()

        posts_data.append({
            'id': post.id,
            'user': post.user.username,
            'handle': f'@{post.user.username}',
            'desc': post.caption,
            'hashtags': post.hashtags,
            'likes': post.like_set.count(),
            'comments': post.comment_set.count(),
            'liked': liked,
            'bookmarked': bookmarked,
            'video_url': video.file.url if video else None,
            'image_url': image.file.url if image else None,
            'has_video': bool(video),
        })

    return render(request, 'user/home.html', {'posts_json': json.dumps(posts_data)})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active and not user.is_superuser:
                return render(request, 'user/login.html', {'error': 'Please verify your email before logging in. Check your inbox for the verification code.'})
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'user/login.html', {'error': 'Invalid username or password'})
    return render(request, 'user/login.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        code = request.POST.get('code')
        resend = request.POST.get('resend')
        ajax = request.POST.get('ajax')

        if resend and email:
            try:
                user = User.objects.get(email=email, is_active=False)
                verification = user.email_verification
                verification.code = str(random.randint(100000, 999999))
                verification.save()
                _send_code(email, verification.code, user)
            except (User.DoesNotExist, EmailVerification.DoesNotExist):
                if ajax:
                    return JsonResponse({'error': 'User not found'}, status=404)
                return render(request, 'user/signup.html', {'error': 'Something went wrong. Please sign up again.'})

            if ajax:
                return JsonResponse({'success': True})
            return render(request, 'user/signup.html', {
                'show_code_input': True,
                'email': email,
                'success': 'A new code has been sent to your email.'
            })

        if code:
            try:
                user = User.objects.get(email=email, is_active=False)
                verification = EmailVerification.objects.get(user=user, code=code)
            except (User.DoesNotExist, EmailVerification.DoesNotExist):
                return render(request, 'user/signup.html', {
                    'show_code_input': True,
                    'email': email,
                    'error': 'Invalid code. Please try again.'
                })
            user.is_active = True
            user.save()
            verification.delete()
            login(request, user)
            return redirect('home')

        existing_email = User.objects.filter(email=email).first()
        if existing_email:
            if existing_email.is_active:
                return render(request, 'user/signup.html', {'error': 'Email already registered'})
            existing_email.delete()

        if User.objects.filter(username=username).exists():
            existing_username = User.objects.get(username=username)
            if existing_username.is_active:
                return render(request, 'user/signup.html', {'error': 'Username already taken'})
            existing_username.delete()

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=False
        )
        verification = EmailVerification.objects.create(user=user)
        _send_code(email, verification.code, user)

        return render(request, 'user/signup.html', {
            'show_code_input': True,
            'email': email,
            'success': 'Account created! Check your email for the verification code.'
        })
    return render(request, 'user/signup.html')

@login_required(login_url='index')
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        name = request.POST.get('name', '').strip()
        bio = request.POST.get('bio', '').strip()
        if username:
            request.user.username = username
        request.user.first_name = name
        request.user.save()
        profile_obj.bio = bio
        if request.FILES.get('profile_picture'):
            profile_obj.profile_picture = request.FILES['profile_picture']
        profile_obj.save()
        return JsonResponse({'success': True})
    posts = request.user.posts.select_related('video', 'image').prefetch_related('like_set', 'comment_set').all().order_by('-created_at')
    bookmarked_ids = Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True)
    bookmarked_posts = Post.objects.filter(id__in=bookmarked_ids).select_related('video', 'image').prefetch_related('like_set', 'comment_set').order_by('-created_at')
    liked_ids = Like.objects.filter(user=request.user).values_list('post_id', flat=True)
    liked_posts = Post.objects.filter(id__in=liked_ids).select_related('video', 'image').prefetch_related('like_set', 'comment_set').order_by('-created_at')
    return render(request, 'user/profile.html', {
        'profile_user': request.user,
        'profile_picture': profile_obj.profile_picture.url if profile_obj.profile_picture else None,
        'bio': profile_obj.bio,
        'name': request.user.first_name,
        'posts': posts,
        'bookmarked_posts': bookmarked_posts,
        'liked_posts': liked_posts,
        'following_count': request.user.following.count(),
        'followers_count': profile_obj.followers.count(),
        'total_likes': sum(p.like_set.count() for p in posts),
    })


def follow_user(request, username):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)
    profile, _ = Profile.objects.get_or_create(user=target_user)
    if request.user in profile.followers.all():
        profile.followers.remove(request.user)
        following = False
    else:
        profile.followers.add(request.user)
        following = True
        Activity.objects.create(
            user=target_user,
            actor=request.user,
            activity_type=Activity.FOLLOW,
            text=f'{request.user.username} started following you.'
        )
    return JsonResponse({
        'following': following,
        'followers_count': profile.followers.count(),
        'following_count': request.user.following.count(),
    })


@login_required(login_url='index')
def following_page(request):
    following_profiles = request.user.following.select_related('user').all()
    followed_ids = set()
    following_list = []
    for pf in following_profiles:
        u = pf.user
        if u == request.user or u.is_superuser:
            continue
        followed_ids.add(u.id)
        following_list.append({
            'username': u.username,
            'handle': f'@{u.username}',
            'bio': pf.bio[:80] if pf.bio else '',
            'avatar': pf.profile_picture.url if pf.profile_picture else None,
        })
    suggested = []
    suggested_users = User.objects.exclude(id__in=followed_ids).exclude(id=request.user.id).exclude(is_superuser=True).select_related('profile')[:20]
    for u in suggested_users:
        try:
            pf = u.profile
        except ObjectDoesNotExist:
            Profile.objects.get_or_create(user=u)
            pf = u.profile
        suggested.append({
            'username': u.username,
            'handle': f'@{u.username}',
            'bio': pf.bio[:80] if pf.bio else '',
            'avatar': pf.profile_picture.url if pf.profile_picture else None,
        })
    return render(request, 'user/following.html', {
        'following_json': json.dumps(following_list),
        'suggested_json': json.dumps(suggested),
        'following_count': len(following_list),
        'following_list': following_list,
        'suggested': suggested,
    })

def explore(request):
    query = request.GET.get('q', '')
    hashtag = request.GET.get('hashtag', '')
    posts = Post.objects.select_related('video', 'image').prefetch_related('like_set', 'comment_set', 'user').all().order_by('-created_at')
    users = User.objects.none()
    if query:
        posts = posts.filter(Q(caption__icontains=query) | Q(hashtags__icontains=query))
        users = User.objects.filter(is_superuser=False, username__icontains=query).exclude(id=request.user.id if request.user.is_authenticated else None)
    if hashtag:
        posts = posts.filter(hashtags__icontains=hashtag)
    posts_data = []
    for post in posts:
        liked = False
        bookmarked = False
        if request.user.is_authenticated:
            liked = post.like_set.filter(user=request.user).exists()
            bookmarked = post.bookmark_set.filter(user=request.user).exists()
        posts_data.append({
            'id': post.id,
            'user': post.user.username,
            'likes': post.like_set.count(),
            'comments': post.comment_set.count(),
            'liked': liked,
            'bookmarked': bookmarked,
            'video_url': post.video.file.url if post.video else None,
            'image_url': post.image.file.url if post.image else None,
            'has_video': bool(post.video),
        })
    users_data = []
    for u in users:
        try:
            pf = u.profile
        except ObjectDoesNotExist:
            Profile.objects.get_or_create(user=u)
            pf = u.profile
        users_data.append({
            'username': u.username,
            'avatar': pf.profile_picture.url if pf.profile_picture else None,
        })
    all_hashtags = set()
    for p in Post.objects.exclude(hashtags='').values_list('hashtags', flat=True):
        for tag in p.split():
            if tag.startswith('#'):
                all_hashtags.add(tag)
    trending_hashtags = sorted(all_hashtags)[:10]
    followed_ids = set()
    if request.user.is_authenticated:
        followed_ids = set(request.user.following.values_list('user_id', flat=True))
    suggestion_users = User.objects.filter(is_superuser=False).select_related('profile')[:20]
    suggestion_data = []
    for u in suggestion_users:
        if u.id in followed_ids:
            stype = 'friend'
        else:
            stype = 'user'
        try:
            pf = u.profile
        except ObjectDoesNotExist:
            Profile.objects.get_or_create(user=u)
            pf = u.profile
        suggestion_data.append({
            'type': stype,
            'label': u.username,
            'avatar': pf.profile_picture.url if pf.profile_picture else None,
        })
    for tag in trending_hashtags[:8]:
        suggestion_data.append({
            'type': 'hashtag',
            'label': tag,
            'avatar': None,
        })
    return render(request, 'user/explore.html', {
        'posts_json': json.dumps(posts_data),
        'users_json': json.dumps(users_data),
        'suggestions_json': json.dumps(suggestion_data),
        'trending_hashtags': trending_hashtags,
        'current_query': query,
        'current_hashtag': hashtag,
    })

@login_required(login_url='index')
def friends(request):
    followed_ids = request.user.following.values_list('user_id', flat=True)
    friends_posts = Post.objects.filter(user_id__in=followed_ids).select_related('video', 'image').prefetch_related('like_set', 'comment_set', 'user').order_by('-created_at')
    friends_activity = Activity.objects.filter(user_id__in=followed_ids).select_related('actor', 'post').order_by('-created_at')[:30]
    posts_data = []
    for post in friends_posts:
        liked = post.like_set.filter(user=request.user).exists()
        bookmarked = post.bookmark_set.filter(user=request.user).exists()
        posts_data.append({
            'id': post.id,
            'user': post.user.username,
            'desc': post.caption,
            'likes': post.like_set.count(),
            'comments': post.comment_set.count(),
            'liked': liked,
            'bookmarked': bookmarked,
            'video_url': post.video.file.url if post.video else None,
            'image_url': post.image.file.url if post.image else None,
            'has_video': bool(post.video),
        })
    activity_data = []
    for a in friends_activity:
        activity_data.append({
            'id': a.id,
            'actor': a.actor.username,
            'type': a.activity_type,
            'text': a.text,
            'time': a.created_at.isoformat(),
            'post_id': a.post_id,
        })
    suggested_users = User.objects.exclude(id__in=followed_ids).exclude(id=request.user.id).exclude(is_superuser=True).select_related('profile')[:10]
    suggested = []
    for u in suggested_users:
        try:
            pf = u.profile
        except ObjectDoesNotExist:
            Profile.objects.get_or_create(user=u)
            pf = u.profile
        suggested.append({
            'username': u.username,
            'handle': f'@{u.username}',
            'bio': pf.bio[:80] if pf.bio else '',
            'avatar': pf.profile_picture.url if pf.profile_picture else None,
        })
    return render(request, 'user/friends.html', {
        'posts_json': json.dumps(posts_data),
        'activity_json': json.dumps(activity_data),
        'suggested': suggested,
    })

def logout_view(request):
    logout(request)
    return redirect('index')
