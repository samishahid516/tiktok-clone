# TikTok Clone — Full Feature Documentation

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Video Upload — How It Works End-to-End](#2-video-upload--how-it-works-end-to-end)
3. [Video Feed — Home Page](#3-video-feed--home-page)
4. [Messaging / Conversations System](#4-messaging--conversations-system)
5. [Profile Update](#5-profile-update)
6. [Like / Bookmark / Comment System](#6-like--bookmark--comment-system)
7. [Authentication & Email Verification](#7-authentication--email-verification)
8. [Django Signals](#8-django-signals)
9. [URL Routes Reference](#9-url-routes-reference)
10. [Database Models](#10-database-models)

---

## 1. Project Overview

Full-stack TikTok clone built with:

| Layer | Technology |
|-------|-----------|
| Backend | Django 6.0.7 (Python) |
| Frontend | Django Templates + Alpine.js |
| Styling | Tailwind CSS v4 |
| Database | SQLite (`db.sqlite3`) |
| Email | Gmail SMTP (App Passwords) |
| File Storage | Local filesystem (`media/`) |

### Apps

- **`core`** — User authentication, profiles, email verification
- **`post`** — Posts (video/image), likes, comments, bookmarks, conversations

### Key Directories

```
tiktok/
├── core/            # Auth & profile logic
│   ├── models.py    # EmailVerification, Profile
│   ├── views.py     # index, home, login, signup, profile
│   └── signals.py   # Auto-create Profile on User signup
├── post/            # Post/media/like/comment logic
│   ├── models.py    # Post, Video, Image, Soundtrack, Like, Comment, Bookmark, CommentLike
│   ├── views.py     # upload, post_detail, like_post, add_comment, toggle_bookmark, conversations
│   ├── forms.py     # PostForm, VideoForm, ImageForm, SoundtrackForm, CommentForm
│   └── signals.py   # File cleanup on delete, logging on create
├── templates/
│   ├── user/
│   │   ├── home.html       # Main video feed (Alpine.js SPA)
│   │   ├── profile.html    # User profile with edit modal + 3 tabs
│   │   ├── index.html      # Landing page
│   │   ├── login.html      # Login form
│   │   └── signup.html     # Signup with email code verification
│   ├── post/
│   │   ├── upload.html     # Upload form (drag-and-drop, preview, settings)
│   │   └── detail.html     # Single post detail view
│   └── emails/
│       └── verify_email.html  # HTML email with verification code
├── tiktok/
│   └── settings.py        # Django config + Gmail SMTP
├── static/                # Tailwind CSS output, Alpine.js, images
└── media/                 # Uploaded videos, images, profile pictures
```

---

## 2. Video Upload — How It Works End-to-End

### 2.1 The Upload Page (`/post/upload/`)

**Template:** `templates/post/upload.html`  
**View:** `post/views.py` → `upload()`  
**Auth:** Required (`@login_required`)

#### Page Layout

- **Drag-and-drop zones** for video and image
- **File selection** via click (hidden `<input type="file">`)
- **File preview** in 9:16 aspect ratio container
- **Details form**: Description, Hashtags, Mention, Location (with autocomplete of Pakistani locations)
- **Settings**: Schedule (now/later), Visibility (Everyone), High-quality toggle
- **Info cards**: Size & Duration, File Formats, Resolutions, Aspect Ratios
- **Post / Discard** buttons

#### Frontend Logic (Alpine.js)

```javascript
x-data="{
    draggingVideo: false,
    draggingImage: false,
    selectedVideo: null,
    selectedImage: null,
    ...
}"
```

- `draggingVideo` / `draggingImage` — toggle visual feedback on drag-over
- `selectedVideo` / `selectedImage` — store the File object after selection
- `descCount` — live character counter for the description textarea
- `filteredLocations()` — filters hardcoded location list by user input
- `highQuality` — toggle for quality preference

#### Drag-and-Drop

```html
<div @dragover.prevent="draggingVideo = true"
     @dragleave.prevent="draggingVideo = false"
     @drop.prevent="draggingVideo = false; $refs.videoInput.files = $event.dataTransfer.files; selectedVideo = $event.dataTransfer.files[0]">
```

The `@drop` handler assigns the dropped file to the hidden input's `files` property and updates `selectedVideo` for preview.

#### File Preview

```html
<template x-if="selectedVideo">
    <video class="w-full h-full object-contain" controls>
        <source :src="URL.createObjectURL(selectedVideo)">
    </video>
</template>
<template x-if="!selectedVideo && selectedImage">
    <img :src="URL.createObjectURL(selectedImage)" class="w-full h-full object-contain">
</template>
```

`URL.createObjectURL()` creates a temporary blob URL for client-side preview without uploading.

### 2.2 Backend Upload Handler

**View:** `post/views.py` `upload()` (line ~20)

```python
@login_required(login_url='index')
def upload(request):
    if request.method == 'POST':
        # DELETE method (send _method=DELETE in form)
        method = request.POST.get('_method', 'POST').upper()
        if method == 'DELETE':
            post_id = request.POST.get('post_id')
            post = get_object_or_404(Post, id=post_id, user=request.user)
            post.delete()
            return redirect('home')

        # CREATE method
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()

            # Save video (if provided)
            video_file = request.FILES.get('video')
            if video_file:
                Video.objects.create(post=post, file=video_file)

            # Save image (if provided)
            image_file = request.FILES.get('image')
            if image_file:
                Image.objects.create(post=post, file=image_file)

            # Save soundtrack name (optional metadata)
            soundtrack_name = request.POST.get('soundtrack', '')
            if soundtrack_name:
                Soundtrack.objects.create(post=post, title=soundtrack_name)

            return redirect('home')
    return render(request, 'post/upload.html')
```

**Flow:**
1. Validate form data using `PostForm` (caption)
2. Create `Post` object with `user` and `caption`
3. Check for uploaded video file → create `Video` record (file saved to `media/user/videos/`)
4. Check for uploaded image file → create `Image` record (file saved to `media/user/images/`)
5. Check for soundtrack name → create `Soundtrack` record
6. Redirect to home feed

### 2.3 The `_method` Pattern

HTML forms only support GET and POST natively. To support DELETE (and PATCH in `post_detail`), the project uses a hidden field convention:

```html
<input type="hidden" name="_method" value="DELETE">
```

The view checks `request.POST.get('_method')` and dispatches accordingly:

```python
method = request.POST.get('_method', 'POST').upper()
if method == 'DELETE':
    # handle delete
elif method == 'PATCH':
    # handle update
```

### 2.4 Post Detail View — Edit & Delete

**View:** `post/views.py` `post_detail()`

Supports:
- **GET** — renders `post/detail.html` showing post metadata and media
- **POST + `_method=PATCH`** — updates caption, soundtrack, video, or image
- **POST + `_method=DELETE`** — deletes post (only by owner)

```python
if method == 'PATCH':
    if post.user != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    form = PostForm(request.POST, instance=post)
    if form.is_valid():
        form.save()
        # Handle soundtrack, video, image updates...
        return JsonResponse({'success': True})
```

### 2.5 File Storage on Disk

| Model | Upload Path |
|-------|------------|
| `Video.file` | `media/user/videos/` |
| `Image.file` | `media/user/images/` |
| `Soundtrack.file` | `media/user/soundtracks/` |
| `Profile.profile_picture` | `media/user/profile_pictures/` |

Configured in `tiktok/settings.py`:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

Served in `tiktok/urls.py`:

```python
+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 2.6 File Cleanup on Delete (Signals)

When a `Post`, `Video`, or `Image` is deleted, the actual file is removed from disk automatically via Django signals:

**`post/signals.py`:**

```python
@receiver(pre_delete, sender=Post)
def post_cleanup(sender, instance, **kwargs):
    for video in instance.videos.all():
        if video.file and os.path.isfile(video.file.path):
            os.remove(video.file.path)
    for image in instance.images.all():
        if image.file and os.path.isfile(image.file.path):
            os.remove(image.file.path)
    for soundtrack in instance.soundtracks.all():
        if soundtrack.file and soundtrack.file.path and os.path.isfile(soundtrack.file.path):
            os.remove(soundtrack.file.path)

@receiver(pre_delete, sender=Video)
def video_cleanup(sender, instance, **kwargs):
    if instance.file and os.path.isfile(instance.file.path):
        os.remove(instance.file.path)

@receiver(pre_delete, sender=Image)
def image_cleanup(sender, instance, **kwargs):
    if instance.file and os.path.isfile(instance.file.path):
        os.remove(instance.file.path)
```

This prevents orphaned files from accumulating in the `media/` directory.

---

## 3. Video Feed — Home Page

**Template:** `templates/user/home.html` (576 lines)  
**View:** `core/views.py` `home()`  
**Auth:** Optional (guests can browse)

### 3.1 How Posts Are Loaded

The `home()` view queries all posts, builds a JSON array with computed fields (like count, comment count, liked/bookmarked status), serializes it, and injects it into the template:

```python
def home(request):
    posts = Post.objects.prefetch_related('videos', 'images', 'likes', 'comments', 'user').all().order_by('-created_at')
    posts_data = []
    for post in posts:
        video = post.videos.first()
        image = post.images.first()
        liked = request.user.is_authenticated and post.likes.filter(user=request.user).exists()
        bookmarked = request.user.is_authenticated and post.bookmarks.filter(user=request.user).exists()
        posts_data.append({
            'id': post.id,
            'user': post.user.username,
            'handle': f'@{post.user.username}',
            'desc': post.caption,
            'likes': post.likes.count(),
            'comments': post.comments.count(),
            'liked': liked,
            'bookmarked': bookmarked,
            'video_url': video.file.url if video else None,
            'image_url': image.file.url if image else None,
            'has_video': bool(video),
        })
    return render(request, 'user/home.html', {'posts_json': json.dumps(posts_data)})
```

The JSON is embedded in the HTML as a script tag:

```html
<script id="posts-data" type="application/json">{{ posts_json|safe }}</script>
```

Alpine.js parses it:

```javascript
videos: JSON.parse(document.getElementById('posts-data').textContent),
```

### 3.2 Video Player — Vertical Feed

The feed is a vertical stack inside a container with `overflow: hidden`. Navigation is done by translating the container vertically:

```html
<div class="transition-transform duration-500 ease-in-out w-full h-full flex flex-col"
     :style="`transform: translateY(-${currentIndex * 100}%)`">
    <template x-for="(video, i) in videos" :key="i">
        <div class="w-full h-full shrink-0 flex items-center justify-center">
            <div class="aspect-[9/16] h-full max-h-[calc(100vh-10px)] ...">
                <video :src="video.video_url" ...></video>
            </div>
        </div>
    </template>
</div>
```

### 3.3 Video Autoplay

On `init()`, the first video plays. When `currentIndex` changes, the new video plays and the previous one pauses:

```javascript
init() {
    this.$nextTick(function() {
        var vs = document.querySelectorAll('video')
        if (vs.length) vs[0].play()
    })
    this.$watch('currentIndex', function(index) {
        this.$nextTick(function() {
            var vs = document.querySelectorAll('video')
            vs.forEach(function(v, i) { i === index ? v.play() : v.pause() })
        })
    })
},
```

Clicking a video toggles play/pause:

```html
<video ... @click="$el.paused ? $el.play() : $el.pause()"></video>
```

### 3.4 Navigation Controls

- **Up/Down arrows** — increment/decrement `currentIndex`
- **Navigation dots** — click to jump to a specific video
- **Keyboard-like buttons** (vertical dots on right side)

```html
<button @click="currentIndex > 0 ? currentIndex-- : null">
    <svg>↑</svg>
</button>
<template x-for="(_, i) in videos">
    <div @click="currentIndex = i" :class="i === currentIndex ? '...' : '...'"></div>
</template>
<button @click="currentIndex < videos.length - 1 ? currentIndex++ : null">
    <svg>↓</svg>
</button>
```

---

## 4. Messaging / Conversations System

### 4.1 Architecture

There is **no real-time chat** or dedicated `Message` model. The "Messages" feature is a **comment-based pseudo-messaging system** that aggregates comments left by other users on the current user's posts.

### 4.2 Backend — `conversations()` View

**Route:** `/post/conversations/`  
**View:** `post/views.py` `conversations()` (line ~190)

```python
@login_required(login_url='index')
def conversations(request):
    comments = Comment.objects.filter(post__user=request.user) \
        .exclude(user=request.user) \
        .select_related('user', 'post') \
        .prefetch_related('likes') \
        .order_by('-created_at')

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
```

**Logic:**
1. Find all comments on the current user's posts (excluding the user's own comments)
2. Deduplicate by commenter — only the most recent comment per user is kept
3. Return as JSON array

### 4.3 Frontend — Messages Panel

**File:** `templates/user/home.html` (lines 121-190)

Triggered by clicking the "Messages" nav item:

```javascript
item.id === 'messages' ? (showMessages = true, fetchConversations()) : null
```

The `fetchConversations()` function calls the API and stores results:

```javascript
fetchConversations() {
    fetch('/post/conversations/')
        .then(r => r.json())
        .then(d => { this.conversations = d.conversations })
},
```

**Panel Layout:**

- **Conversation list**: avatar (first letter), username, last comment text, date
- **Empty state**: "No messages yet" with explanatory text
- **Detail view**: clicking a conversation shows the full comment with:
  - Username + avatar
  - Comment text
  - Timestamp
  - Like button (toggles `CommentLike`)
  - Reply input

### 4.4 Reply Flow

When replying in the messages panel, the app posts a new comment to the original post:

```javascript
sendReply(conv) {
    fetch('/post/' + conv.post_id + '/comment/', {
        method: 'POST',
        headers: { 'X-CSRFToken': this.csrfToken, 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'text=' + encodeURIComponent(this.replyText)
    })
}
```

This uses the same `add_comment` endpoint that handles regular comments, but without a `parent_id`, so it appears as a top-level comment on the post (not a threaded reply to the original comment).

### 4.5 Limitations

- No private 1-on-1 messaging
- No real-time updates (WebSocket)
- No typing indicators or read receipts
- Replies don't thread under the original comment in the messages panel

---

## 5. Profile Update

### 5.1 Profile Page

**Route:** `/profile/`  
**View:** `core/views.py` `profile()`  
**Template:** `templates/user/profile.html`  
**Auth:** Required (`@login_required`)

### 5.2 Profile Model

```python
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='user/profile_pictures/', blank=True, null=True)
    followers = models.ManyToManyField(User, related_name='following', blank=True)
```

A `Profile` is auto-created when a `User` signs up via a Django signal (`core/signals.py`).

### 5.3 Editing Profile — Backend

```python
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

    # GET: render profile page
    return render(request, 'user/profile.html', {
        'profile_user': request.user,
        'profile_picture': profile_obj.profile_picture.url if profile_obj.profile_picture else None,
        'bio': profile_obj.bio,
        'name': request.user.first_name,
        'posts': posts,
        'bookmarked_posts': bookmarked_posts,
        'liked_posts': liked_posts,
    })
```

**Editable fields:**
- **Username** — stored on `User.username`
- **Name** — stored on `User.first_name`
- **Bio** — stored on `Profile.bio`
- **Profile picture** — stored on `Profile.profile_picture`

### 5.4 Editing Profile — Frontend (Alpine.js Modal)

The modal is controlled by `showEditProfile`. Form fields are bound to Alpine.js properties:

```javascript
editUsername: '{{ profile_user.username }}',
editName: '{{ name|default:"" }}',
editBio: '{{ bio|default:"" }}',
```

The modal includes:
- **Change photo** button → file input for `profile_picture`
- **Username** input with live preview of profile URL
- **Name** input with constraint hint
- **Bio** textarea (max 80 chars) with live character counter

#### Save Flow

```javascript
saveProfile() {
    var form = document.getElementById('editProfileForm');
    var data = new FormData(form);
    fetch(form.action, {
        method: 'POST',
        body: data,
        headers: { 'X-CSRFToken': '{{ csrf_token }}' }
    }).then(r => r.json()).then(d => {
        if (d.success) {
            this.showEditProfile = false;
            location.reload()
        }
    })
}
```

1. Collect form data (including file upload) via `FormData`
2. Send as multipart POST to `/profile/`
3. On success, close modal and reload the page

### 5.5 "No bio yet." Fallback

The bio display uses conditional rendering:

```html
<p class="text-sm text-neutral-500 mt-3">
    {% if bio %}{{ bio }}{% else %}No bio yet.{% endif %}
</p>
```

### 5.6 Profile Tabs

The profile has 3 tabs:

| Tab | Content | Data Source |
|-----|---------|-------------|
| **Videos** | User's own posts | `request.user.posts.all()` |
| **Favorites** | Bookmarked posts | `Bookmark.objects.filter(user=request.user)` |
| **Liked** | Liked posts | `Like.objects.filter(user=request.user)` |

Tab switching is done with Alpine.js and CSS transitions:

```javascript
switchTab(tab) {
    var order = ['videos', 'favorites', 'liked'];
    this.tabDirection = order.indexOf(tab) > order.indexOf(this.activeTab) ? 'left' : 'right';
    this.prevTab = this.activeTab;
    this.activeTab = tab
}
```

**Note:** The Following / Followers / Likes counts in the profile header are currently hardcoded to `0` — they are not yet connected to the actual data.

---

## 6. Like / Bookmark / Comment System

### 6.1 Like

**Route:** `/post/<id>/like/`  
**View:** `post/views.py` `like_post()`  
**Method:** POST only

```python
@login_required(login_url='index')
@require_http_methods(['POST'])
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'total_likes': post.likes.count()})
```

Toggle behavior: if the like exists, delete it (unlike); if not, create it (like).

**Frontend:**

```javascript
toggleLike(i) {
    fetch('/post/' + v.id + '/like/', { method: 'POST', headers: { 'X-CSRFToken': this.csrfToken } })
        .then(r => r.json())
        .then(function(d) {
            setTimeout(function() {
                v.liked = d.liked
                v.likes = d.total_likes
            }, 500)
        })
    this.toast(v.liked ? 'Unliked' : 'Liked!')
}
```

The like button visually updates (filled red heart + count change) with a 500ms delay for animation.

### 6.2 Bookmark

**Route:** `/post/<id>/bookmark/`  
**View:** `post/views.py` `toggle_bookmark()`  
**Method:** POST only

Same toggle pattern as likes. Returns `{'bookmarked': true/false}`.

**Frontend:** The bookmark button toggles a yellow fill on the icon. Shows toast: "Added to favorites!" / "Removed from favorites".

### 6.3 Comment

#### Fetching Comments (GET)

**Route:** `/post/<id>/comment/`  
**View:** `post/views.py` `add_comment()`  
**Method:** GET

Returns threaded comments with nested replies:

```python
def add_comment(request, post_id):
    if request.method == 'GET':
        comments = post.comments.filter(parent=None) \
            .select_related('user') \
            .prefetch_related('replies__user', 'likes') \
            .order_by('-created_at')
        data = []
        for c in comments:
            replies_data = [...]
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
```

#### Adding a Comment (POST)

```python
if form.is_valid():
    comment = form.save(commit=False)
    comment.user = request.user
    comment.post = post
    parent_id = request.POST.get('parent_id')
    if parent_id:
        comment.parent_id = parent_id  # Threaded reply
    comment.save()
    return JsonResponse({...})
```

**Frontend - Comments Panel:**

- Slide-in panel from the right
- Shows all comments with reply counts
- Each comment can be liked, replied to, or have replies expanded
- New comments appear at the top of the list

#### Comment Likes

**Route:** `/post/comment/<id>/like/`  
**View:** `post/views.py` `like_comment()`  
**Method:** POST only

Uses a separate `CommentLike` model (different from `Like` which is for posts). Toggle behavior identical to post likes.

---

## 7. Authentication & Email Verification

### 7.1 Signup Flow

```
User fills signup form → User created (is_active=False) → 6-digit code emailed
                                                                   ↓
User enters code → Code verified → User activated → Auto-login → Home
```

### 7.2 Email Verification Model

```python
class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(random.randint(100000, 999999))
        super().save(*args, **kwargs)
```

### 7.3 Email Sending

```python
def _send_code(email, code, user):
    subject = 'Your TikTok verification code'
    html_message = render_to_string('emails/verify_email.html', {'user': user, 'code': code})
    plain_message = strip_tags(html_message)
    send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [email], html_message=html_message)
```

### 7.4 Code Auto-Resend (Alpine.js)

After signup, a 60-second countdown starts. When it reaches 0, the code auto-resends via AJAX:

```javascript
init() { this.startTimer() },
startTimer() {
    this.interval = setInterval(() => {
        this.timer--;
        if (this.timer <= 0) {
            clearInterval(this.interval);
            this.canResend = true;
            this.autoResend();  // Fetch POST to /signup/ with resend=1
        }
    }, 1000)
},
autoResend() {
    const data = new FormData(this.$refs.autoForm);
    data.append('ajax', '1');
    fetch('/signup/', { method: 'POST', body: data })
        .then(r => r.json())
        .then(resp => {
            if (resp.success) {
                this.timer = 60;
                this.canResend = false;
                this.startTimer();
            }
        })
}
```

### 7.5 Re-Registration

Users who signed up but never verified (inactive) can re-register with the same email/username. The old inactive record is deleted.

### 7.6 Login

Standard Django authentication. Inactive users (unverified) are blocked with a specific error message.

### 7.7 Gmail SMTP Configuration

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your.email@gmail.com'
EMAIL_HOST_PASSWORD = '16-char-app-password'
DEFAULT_FROM_EMAIL = 'TikTok <your.email@gmail.com>'
```

---

## 8. Django Signals

### 8.1 `core/signals.py` — Auto-Create Profile

```python
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
```

| Trigger | Action |
|---------|--------|
| New User created | `Profile` auto-created |

### 8.2 `post/signals.py` — File Cleanup & Logging

| Trigger | Action |
|---------|--------|
| `Post.created` | Logs: "New post created by {username}" |
| `Post.pre_delete` | Deletes associated video/image/soundtrack files from disk |
| `Video.pre_delete` | Deletes the video file from disk |
| `Image.pre_delete` | Deletes the image file from disk |
| `Like.created` | Logs: "{username} liked post {id}" |
| `Comment.created` | Logs: "{username} commented on post {id}" |

---

## 9. URL Routes Reference

### 9.1 Core App (`core/urls.py`)

| URL | Methods | View | Auth | Description |
|-----|---------|------|------|-------------|
| `/` | GET | `index` | No | Landing page |
| `/home/` | GET | `home` | No | Video feed |
| `/login/` | GET, POST | `login_view` | No | Login |
| `/signup/` | GET, POST | `signup` | No | Signup + code verify |
| `/logout/` | GET | `logout_view` | No | Logout |
| `/profile/` | GET, POST | `profile` | Yes | Profile page + edit |

### 9.2 Post App (`post/urls.py`)

| URL | Methods | View | Auth | Description |
|-----|---------|------|------|-------------|
| `/post/upload/` | GET, POST | `upload` | Yes | Upload video/image |
| `/post/<id>/` | GET, POST | `post_detail` | Yes | Detail, edit (PATCH), delete |
| `/post/<id>/like/` | POST | `like_post` | Yes | Toggle like |
| `/post/<id>/bookmark/` | POST | `toggle_bookmark` | Yes | Toggle bookmark |
| `/post/<id>/comment/` | GET, POST | `add_comment` | Yes | List/add comments |
| `/post/comment/<id>/like/` | POST | `like_comment` | Yes | Toggle comment like |
| `/post/conversations/` | GET | `conversations` | Yes | Messages list |

### 9.3 Root (`tiktok/urls.py`)

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('post/', include('post.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 10. Database Models

### 10.1 `core/models.py`

**EmailVerification**
| Field | Type | Notes |
|-------|------|-------|
| user | OneToOneField(User) | Linked user |
| code | CharField(6) | 6-digit random code |
| created_at | DateTimeField | Auto-set |

**Profile**
| Field | Type | Notes |
|-------|------|-------|
| user | OneToOneField(User) | Linked user |
| bio | TextField | Blank allowed |
| profile_picture | ImageField | Uploaded to `user/profile_pictures/` |
| followers | ManyToManyField(User) | Following system |

### 10.2 `post/models.py`

**Post** (central model — all media and interactions link through here)
| Field | Type | Notes |
|-------|------|-------|
| user | ForeignKey(User) | Post owner |
| video | ForeignKey(Video, null) | Direct FK to the single Video (was reverse FK) |
| image | ForeignKey(Image, null) | Direct FK to the single Image (was reverse FK) |
| soundtrack | ForeignKey(Soundtrack, null) | Direct FK to the single Soundtrack (was reverse FK) |
| likes | ManyToManyField(User, through=Like) | Convenience access to Users who liked |
| comments | ManyToManyField(User, through=Comment) | Convenience access to Users who commented |
| caption | TextField | Post description |
| hashtags | CharField(200) | Stored as text, e.g. "#romantic #couple" |
| created_at | DateTimeField | Auto-set |
| updated_at | DateTimeField | Auto-updated on save |

**Video** (standalone — no FK back to Post)
| Field | Type | Notes |
|-------|------|-------|
| file | FileField | Uploaded to `user/videos/` |
| created_at | DateTimeField | Auto-set |

**Image** (standalone — no FK back to Post)
| Field | Type | Notes |
|-------|------|-------|
| file | ImageField | Uploaded to `user/images/` |
| created_at | DateTimeField | Auto-set |

**Soundtrack** (standalone — no FK back to Post)
| Field | Type | Notes |
|-------|------|-------|
| title | CharField(255) | Track name |
| artist | CharField(255) | Optional |
| file | FileField | Optional audio file |
| created_at | DateTimeField | Auto-set |

**Like** (through model for Post.likes M2M)
| Field | Type | Notes |
|-------|------|-------|
| user | ForeignKey(User) | Who liked |
| post | ForeignKey(Post, related_name='like_set') | Liked post |
| created_at | DateTimeField | Auto-set |
| *Meta* | unique_together | (user, post) |

**Comment** (through model for Post.comments M2M)
| Field | Type | Notes |
|-------|------|-------|
| user | ForeignKey(User) | Who commented |
| post | ForeignKey(Post, related_name='comment_set') | Commented post |
| parent | ForeignKey('self') | Nullable — threaded replies |
| text | TextField | Comment content |
| created_at | DateTimeField | Auto-set |

**Bookmark**
| Field | Type | Notes |
|-------|------|-------|
| user | ForeignKey(User) | Who bookmarked |
| post | ForeignKey(Post, related_name='bookmark_set') | Bookmarked post |
| created_at | DateTimeField | Auto-set |
| *Meta* | unique_together | (user, post) |

**CommentLike**
| Field | Type | Notes |
|-------|------|-------|
| user | ForeignKey(User) | Who liked |
| comment | ForeignKey(Comment) | Liked comment |
| created_at | DateTimeField | Auto-set |
| *Meta* | unique_together | (user, comment) |

### 10.3 Model Restructuring Rationale

Originally, Video, Image, and Soundtrack had a `post = ForeignKey(Post)` field (one-to-many: one Post could have many Videos). This was changed so that **Post** holds the FK to Video/Image/Soundtrack instead:

```
Before:  Video.post ──→ Post     (one-to-many)
After:   Post.video ──→ Video    (many-to-one from Post side)
```

**Why the change:**

1. **Single media per post** — a post realistically has one video, one image, one soundtrack. The old one-to-many design allowed multiples but the code only ever used `.first()`. The new design enforces this at the model level.

2. **Simpler access** — `post.video` instead of `post.videos.first()`, `post.soundtrack.title` instead of `post.soundtracks.first().title`. No need to null-check a queryset then call `.first()`.

3. **Cleaner prefetching** — `select_related('video', 'image', 'soundtrack')` performs a single JOIN instead of separate prefetch queries.

For likes and comments, the reverse FK `related_name` was changed from `likes`/`comments` to `like_set`/`comment_set` because the new M2M fields on Post now own those names:

- `post.likes` → M2M to User objects (who liked)
- `post.like_set` → queryset of Like objects (the through model)
- Use `post.like_set` anywhere you need to filter/count Like records directly

**Migration impact:** The migration (`0005`) removes the `post` FK from Video/Image/Soundtrack tables, adds `video`/`image`/`soundtrack` FK columns to the Post table, and updates the `post` FK `related_name` on Like/Comment/Bookmark. Existing data is preserved where possible — since one-to-many was never actually used for multiple media, the first video/image/soundtrack per post becomes the new FK value.

## 11. Activity / Notifications Panel

### 11.1 Purpose

The activity panel provides a unified notification feed showing who liked, commented on, mentioned, or followed the current user. It lives in the sidebar of the home feed (`home.html`) and fetches data from a dedicated REST endpoint.

### 11.2 Why This Approach

**Model-backed, not ad-hoc:**

Rather than scraping likes/comments/follows on every page load (which is expensive and doesn't scale), a dedicated `Activity` model (`core/models.py`) records each event at the moment it happens using Django signals. This gives us:

- **O(1) reads** — the activity feed is a simple filtered query on one table
- **Clean separation** — activity creation is decoupled from views; signals fire automatically on the relevant model save
- **Future-ready** — adding new activity types (e.g. `share`, `reply`) is just a new choice + a signal handler

### 11.3 The Activity Model

`core/models.py`:

```python
class Activity(models.Model):
    class Type(models.TextChoices):
        LIKE = 'like'
        COMMENT = 'comment'
        FOLLOW = 'follow'
        MENTION = 'mention'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actor')
    activity_type = models.CharField(max_length=10, choices=Type.choices)
    post = models.ForeignKey('post.Post', null=True, blank=True, on_delete=models.CASCADE)
    comment = models.ForeignKey('post.Comment', null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
```

Key design decisions:
- **`user`** — the *recipient* of the notification (post owner, profile owner)
- **`actor`** — who performed the action
- **`post` / `comment`** — optional foreign keys so the frontend can link back to the relevant content
- **`ordering = ['-created_at']`** — newest activity first, always

### 11.4 Signal Handlers — Activity Creation

**Like → Activity** (`post/signals.py`):

```python
@receiver(post_save, sender=Like)
def create_like_activity(sender, instance, created, **kwargs):
    if created and instance.post.user != instance.user:
        Activity.objects.create(
            user=instance.post.user,
            actor=instance.user,
            activity_type=Activity.Type.LIKE,
            post=instance.post,
        )
```

The `instance.post.user != instance.user` guard prevents self-generated activity (liking your own post doesn't create a notification).

**Comment → Activity + @mention detection** (`post/signals.py`):

```python
@receiver(post_save, sender=Comment)
def create_comment_activity(sender, instance, created, **kwargs):
    if created:
        if instance.post.user != instance.user:
            Activity.objects.create(
                user=instance.post.user,
                actor=instance.user,
                activity_type=Activity.Type.COMMENT,
                post=instance.post,
                comment=instance,
            )
        mentions = re.findall(r'@(\w+)', instance.text)
        for username in mentions:
            try:
                mentioned = User.objects.get(username=username)
                if mentioned != instance.user:
                    Activity.objects.create(
                        user=mentioned,
                        actor=instance.user,
                        activity_type=Activity.Type.MENTION,
                        post=instance.post,
                        comment=instance,
                    )
            except User.DoesNotExist:
                pass
```

Comments generate two kinds of activity:
1. A `comment` activity for the post owner
2. A `mention` activity for each `@username` found in the comment text (excluding self)

**Follow → Activity** (`core/signals.py`):

```python
@receiver(m2m_changed, sender=Profile.followers.through)
def create_follow_activity(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for follower_id in pk_set:
            follower = User.objects.get(id=follower_id)
            if follower != instance.user:
                Activity.objects.create(
                    user=instance.user,
                    actor=follower,
                    activity_type=Activity.Type.FOLLOW,
                )
```

Uses `m2m_changed` (not `post_save`) because `followers` is a ManyToMany field. The `pk_set` contains the IDs of users who were just added as followers.

### 11.5 The API Endpoint

`post/views.py` `activities()`:

```python
@login_required
def activities(request):
    qs = Activity.objects.filter(user=request.user).select_related('actor', 'post', 'comment')
    atype = request.GET.get('type')
    if atype and atype in dict(Activity.Type.choices):
        qs = qs.filter(activity_type=atype)
    data = []
    for a in qs:
        data.append({
            'id': a.id,
            'actor': a.actor.username,
            'actor_picture': getattr(a.actor.profile, 'profile_picture', None) and a.actor.profile.profile_picture.url,
            'type': a.activity_type,
            'post_id': a.post.id if a.post else None,
            'comment_preview': (a.comment.text[:60] + '...') if a.comment and len(a.comment.text) > 60 else (a.comment.text if a.comment else None),
            'created_at': a.created_at.isoformat(),
        })
    return JsonResponse({'activities': data})
```

**Query string filtering:**

| `?type=` | Returns |
|----------|---------|
| *(none)* | All activity types (default) |
| `like` | Only likes |
| `comment` | Only comments |
| `follow` | Only follows |
| `mention` | Only @mentions |

The `select_related('actor', 'post', 'comment')` prefetch avoids N+1 queries.

### 11.6 Frontend — Activity Panel

**File:** `templates/user/home.html`

The panel lives inside the sidebar, controlled by Alpine.js state:

```javascript
showActivity: false,
activities: [],
activityFilter: 'all',
```

**Fetching activities:**

```javascript
fetchActivities(type) {
    this.activityFilter = type || 'all';
    fetch('/post/activities/' + (type ? '?type=' + type : ''))
        .then(r => r.json())
        .then(d => { this.activities = d.activities })
},
```

The sidebar nav calls this when the "Activity" item is clicked:

```javascript
item.id === 'activity' ? (showActivity = true, fetchActivities()) : null
```

**Mutual exclusion with Messages panel:**

```javascript
item.id === 'messages' ? (showMessages = true, fetchConversations(), showActivity = false) : null
item.id === 'activity' ? (showActivity = true, fetchActivities(), showMessages = false) : null
```

Only one panel is open at a time — opening activity closes messages and vice versa.

**Filter tabs:**

Five filter buttons at the top of the panel (`flex-wrap` for responsive layout):

| Button | `type` value passed |
|--------|-------------------|
| All activity | *(none)* |
| Likes | `like` |
| Comments | `comment` |
| Mentions and tags | `mention` |
| Followers | `follow` |

Each button calls `fetchActivities(type)` on `@click` and highlights when `activityFilter` matches.

**Activity items:**

Each activity renders differently based on its `type`:

- **Like** — "{actor} liked your post" + post thumbnail link
- **Comment** — "{actor} commented: {comment_preview}" + post link
- **Mention** — "{actor} mentioned you in a comment" + post link  
- **Follow** — "{actor} started following you" (no post link)

**Empty states:**

A per-type empty state system using `x-if` + a dictionary object:

```javascript
emptyMessages: {
    all: { icon: 'bell-slash', title: 'No activity yet', text: 'When someone likes your post, comments, or follows you, it will show up here.' },
    like: { icon: 'heart-slash', title: 'No likes yet', text: 'When someone likes your post, it will appear here.' },
    // ...
},
```

Each tab shows a contextually appropriate icon, title, and description when there are zero matching activities.

### 11.7 Workflow Summary

```
User performs action (like, comment, follow)
         ↓
Model saved (Like, Comment, or m2m on Profile.followers)
         ↓
Signal fires → Activity.objects.create(...)
         ↓
Frontend calls GET /post/activities/?type=like
         ↓
View queries Activity model, returns JSON
         ↓
Alpine.js renders the panel with matching items + empty states
```

### 11.8 Design Rationale

| Concern | Decision | Why |
|---------|----------|-----|
| Storage | Dedicated `Activity` model | Avoids expensive cross-table queries on every page load |
| Timing | Signal-based creation | Guarantees every event is recorded; no manual `activity.save()` calls in views |
| Filtering | `?type=` query param | Simple, cacheable, no extra route needed |
| Frontend state | Alpine.js `x-data` | No page reload needed; matches existing SPA pattern in `home.html` |
| Mutual exclusion | `showActivity` / `showMessages` booleans | Prevents layout conflicts in the sidebar |
| Empty states | Per-tab icon + message dictionary | Better UX than a generic "no results" — user knows the panel is working, just empty for that type |

---

## Appendix: How to Run

```bash
# Start Django server
py manage.py runserver

# Tailwind CSS live updates (separate terminal)
npm run tw:watch
```
