# TikTok Clone — Model Restructuring

## Post is now the main class

Every media and interaction type links **through** `Post`, not the other way around. Post holds direct ForeignKeys to Video/Image/Soundtrack and ManyToManyFields (through Like/Comment) for interactions.

---

## What changed in `post/models.py`

### Video — `post` FK removed

```diff
- post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='videos')
```

Video no longer points to Post. Now **Post has the FK** → `post.video` (added below).

### Image — `post` FK removed

```diff
- post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
```

Now **Post has the FK** → `post.image`.

### Soundtrack — `post` FK removed

```diff
- post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='soundtracks')
```

Now **Post has the FK** → `post.soundtrack`.

### Like — `post` FK kept, `related_name` changed + M2M added on Post

```diff
- post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
+ post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='like_set')
```

The `post` FK still exists on Like (it's the through model). But now **Post also has**: `likes = ManyToManyField(User, through=Like)` so you can access users who liked directly via `post.likes.all()`.

### Comment — `post` FK kept, `related_name` changed + M2M added on Post

```diff
- post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
+ post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comment_set')
```

Same as Like — `post` FK stays on Comment, and **Post also has**: `comments = ManyToManyField(User, through=Comment)`.

### Bookmark — `post` FK kept, `related_name` changed + M2M added on Post

```diff
- post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarks')
+ post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmark_set')
```

Bookmark's `post` FK stays. **Post now also has**: `bookmarks = ManyToManyField(User, through=Bookmark)` so you can access users who bookmarked directly via `post.bookmarks.all()`.

### CommentLike — unchanged

CommentLike still has `comment = ForeignKey(Comment)` and `user = ForeignKey(User)` — no direct `post` FK. No changes.

### Post — all new fields added

```diff
+ video = models.ForeignKey(Video, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
+ image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
+ soundtrack = models.ForeignKey(Soundtrack, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
+ likes = models.ManyToManyField(User, through=Like, related_name='liked_posts', blank=True)
+ comments = models.ManyToManyField(User, through=Comment, related_name='commented_posts', blank=True)
+ bookmarks = models.ManyToManyField(User, through=Bookmark, related_name='bookmarked_posts', blank=True)
+ hashtags = models.CharField(max_length=200, blank=True)
+ updated_at = models.DateTimeField(auto_now=True)
```

Post now **owns** all relationships — media as direct FKs, interactions as M2M through models.

### Post — `__str__` unchanged

```python
def __str__(self):
    return f"{self.user.username}'s post - {self.created_at}"
```

### Which models have `created_at` / `updated_at`

| Model | `created_at` | `updated_at` |
|-------|:-----------:|:-----------:|
| Post | ✅ | ✅ (`auto_now`) |
| Video | ✅ | ❌ |
| Image | ✅ | ❌ |
| Soundtrack | ✅ | ❌ |
| Like | ✅ | ❌ |
| Comment | ✅ | ❌ |
| Bookmark | ✅ | ❌ |
| CommentLike | ✅ | ❌ |

Only `Post` has `updated_at` — it uses `auto_now=True` so it updates automatically every time the post is saved.

---

## Old vs New Access Patterns

| What you want | Old code | New code |
|---------------|----------|----------|
| Post's video | `post.videos.first()` | `post.video` |
| Post's image | `post.images.first()` | `post.image` |
| Post's soundtrack | `post.soundtracks.first()` | `post.soundtrack` |
| Post's soundtrack title | `post.soundtracks.first().title` | `post.soundtrack.title` |
| Like objects | `post.likes.filter(...)` | `post.like_set.filter(...)` |
| Comment objects | `post.comments.filter(...)` | `post.comment_set.filter(...)` |
| Bookmark objects | `post.bookmarks.filter(...)` | `post.bookmark_set.filter(...)` |
| Users who liked | *(not available)* | `post.likes.all()` (M2M) |
| Users who commented | *(not available)* | `post.comments.all()` (M2M) |
| Users who bookmarked | *(not available)* | `post.bookmarks.all()` (M2M) |
| Like count | `post.likes.count()` | `post.like_set.count()` |
| Comment count | `post.comments.count()` | `post.comment_set.count()` |
| Post created date | `post.created_at` | `post.created_at` (unchanged) |
| Post last updated | *(did not exist)* | `post.updated_at` |

---

## Why

1. **Single media per post** — a post has one video/image/soundtrack. The FK on Post enforces this at the model level instead of relying on `.first()` everywhere.

2. **Simpler queries** — `post.video` instead of `post.videos.first()` — no queryset overhead.

3. **Faster joins** — `select_related('video', 'image', 'soundtrack')` uses a single SQL JOIN instead of separate `prefetch_related` queries.

4. **M2M convenience** — `post.likes.all()` gives User objects directly; `post.like_set` gives full Like records when needed.
