
<div align="center">

# TikTok Clone (Python)

A full-stack social media web application built with Django — featuring a vertical video feed, user authentication with email verification, social interactions, and a responsive dark-mode UI.

[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4-06B6D4?style=for-the-badge&logo=tailwindcss)](https://tailwindcss.com/)
[![Alpine.js](https://img.shields.io/badge/Alpine.js-3-8BC0D0?style=for-the-badge&logo=alpine.js)](https://alpinejs.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Screenshots](#screenshots)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the App](#running-the-app)
- [Project Structure](#project-structure)
- [Pages & Routes](#pages--routes)
- [Data Models](#data-models)
- [Management Commands](#management-commands)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This is a **fully functional TikTok clone** built from scratch using Django. It allows users to:

- Sign up and log in with **email verification**
- Upload and share **videos and images**
- Scroll through a **vertical video feed** (just like TikTok)
- **Like, comment, bookmark, and share** posts
- **Follow** other users and see posts from **friends** (mutual follows)
- Search for **users, videos, and hashtags**
- Receive **activity notifications** for likes, comments, follows, and mentions
- Toggle between **light and dark mode**

Whether you're learning Django or looking for a social media starter project, this codebase demonstrates modern Django patterns including custom signals, AJAX interactions, template components, and responsive design.

---

## Features

### Core Functionality

| Feature | Description |
|---|---|
| **Video Feed** | Vertical TikTok-style scrolling with keyboard and mouse wheel navigation |
| **Authentication** | Signup, login, logout with email verification (6-digit code via SMTP) |
| **Post Creation** | Upload videos or images with captions, hashtags, mentions, and soundtracks |
| **Privacy Controls** | Set posts to Everyone, Friends Only, or Only Me |
| **Scheduled Posts** | Schedule posts for a future date and time |
| **Like / Unlike** | Toggle likes on posts and comments |
| **Comments** | Add comments with nested threaded replies |
| **Bookmarks** | Save posts to a favorites tab on your profile |
| **Follow System** | Follow/unfollow users with mutual follow detection (Friends) |
| **User Profiles** | Custom bio, profile picture, stats, and edit modal |
| **Public Profiles** | View any user's profile with their posts in a grid |
| **Explore Page** | Search for videos, users, and hashtags with live suggestions |
| **Friends Feed** | See posts from users you follow who also follow you back |
| **Activity Feed** | Notifications for likes, comments, follows, and mentions |
| **Conversations** | Threaded comment-based messaging between users |
| **Dark Mode** | Toggle persisted in localStorage |
| **Responsive Design** | Collapsible sidebar, mobile-friendly layout |

### Technical Highlights

- **AJAX-powered interactions** — like, comment, follow, bookmark, and search without page reloads
- **Django Signals** — auto-create profiles, clean up media on delete, generate activity notifications
- **Custom Management Commands** — load soundtracks from the command line
- **Tailwind CSS v4** — modern utility-first styling with CLI-based build
- **Alpine.js** — lightweight JavaScript for interactive UI components

---

## Tech Stack

### Backend

| Technology | Purpose |
|---|---|
| **Python 3** | Programming language |
| **Django 6.0.7** | Web framework (MVT architecture) |
| **SQLite** | Database (development) |
| **Django Template Engine** | Server-side HTML rendering |
| **SMTP (Gmail)** | Email verification |

### Frontend

| Technology | Purpose |
|---|---|
| **Tailwind CSS v4** | Utility-first CSS framework |
| **Alpine.js v3** | Lightweight JavaScript interactivity |
| **HTML5** | Structure and semantics |

### Development Tools

| Tool | Purpose |
|---|---|
| **Node.js / npm** | Tailwind CSS CLI dependency |
| **Git** | Version control |

---

## Screenshots

> **Note:** Add your own screenshots to the `screenshots/` folder and they will appear below.  
> Recommended: capture each page at 1920×1080 or 1280×720.

| Page | Preview |
|---|---|
| **Landing Page** — Login/signup splash screen | `screenshots/landing.png` |
| **Login** — Email/username and password form | `screenshots/login.png` |
| **Signup** — Registration with email verification | `screenshots/signup.png` |
| **Home Feed** — Vertical video feed with interactions | `screenshots/home.png` |
| **Explore** — Search with hashtags and live suggestions | `screenshots/explore.png` |
| **Profile** — Own profile with stats and tabs | `screenshots/profile.png` |
| **Public Profile** — Other user's profile with follow button | `screenshots/public_profile.png` |
| **Following** — Followed users and suggestions | `screenshots/following.png` |
| **Friends** — Mutual follows' posts | `screenshots/friends.png` |
| **Post Detail** — Full post view with comments | `screenshots/post_detail.png` |
| **Upload** — Create post with drag-and-drop | `screenshots/upload.png` |
| **Activity Feed** — Notifications panel | `screenshots/activities.png` |
| **Conversations** — Messaging panel | `screenshots/conversations.png` |
| **Dark Mode** — Same pages in dark theme | `screenshots/dark_mode.png` |

---

## Getting Started

### Prerequisites

Make sure you have the following installed on your system:

- **Python 3.10+** — [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** — [Download Node.js](https://nodejs.org/) (required for Tailwind CSS)
- **Git** — [Download Git](https://git-scm.com/downloads)
- A **code editor** (VS Code recommended)

### Installation

Follow these steps to get the project running on your local machine.

#### 1. Clone the repository

```bash
git clone https://github.com/yourusername/tiktok-clone.git
cd tiktok-clone
```

#### 2. Set up a virtual environment

A virtual environment keeps your project dependencies isolated.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt.

#### 3. Install Python dependencies

Create a `requirements.txt` file (if not present) with:

```txt
Django>=6.0,<7.0
Pillow
```

Then run:

```bash
pip install -r requirements.txt
```

> **What these do:**
> - `Django` — the web framework
> - `Pillow` — Python imaging library for handling profile pictures

#### 4. Install Node.js dependencies

```bash
npm install
```

This installs Tailwind CSS and the CLI tool for building stylesheets.

#### 5. Build Tailwind CSS

```bash
npm run tw:build
```

This compiles `static/src/input.css` into `static/src/output.css`.

#### 6. Run database migrations

```bash
python manage.py migrate
```

This creates all the database tables (users, posts, likes, comments, etc.).

#### 7. Create a superuser (admin)

```bash
python manage.py createsuperuser
```

You'll be prompted to enter a username, email, and password. This gives you access to the Django admin panel at `/admin/`.

### Configuration

#### Email Verification (Optional but Recommended)

To enable email verification during signup, configure your email settings in `tiktok/settings.py`. The project is pre-configured for Gmail SMTP:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

> **For Gmail:** You'll need an [App Password](https://support.google.com/accounts/answer/185833) (not your regular password).  
> Enable 2-Factor Authentication on your Google account, then generate an App Password.

If you skip this step, the app will still work — but email verification codes won't be sent. You can manually verify users from the Django admin panel.

### Running the App

Start the development server:

```bash
python manage.py runserver
```

Open your browser and visit: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

#### What to do first:

1. Visit the landing page
2. Click **Sign Up** and create an account
3. Upload a video or image from the **Upload** page (top-right corner)
4. Explore the **Home** feed to see your post
5. Visit your **Profile** to edit your bio and picture
6. Search for users on the **Explore** page
7. Follow other users and check the **Friends** page

---

## Project Structure

```
📁 tiktok-clone/
```

The project is organized into **5 main Django apps/folders** — each with a clear responsibility:

---

### 🧠 `core/` — Authentication, Profiles & Activity

Handles user accounts, profiles, social graph, and notifications.

| File | What it does |
|------|-------------|
| `models.py` | `EmailVerification`, `Profile` (with followers), `Activity` (notifications) |
| `views.py` | Login, signup, home feed, profile, following, explore, friends pages |
| `urls.py` | All `/` routes (home, login, signup, profile, explore, etc.) |
| `signals.py` | Auto-creates a Profile when a new user registers |
| `admin.py` | Registers `EmailVerification` in the Django admin panel |
| `migrations/` | Database schema change history |

---

### 🎬 `post/` — Posts, Media & Social Interactions

The heart of the app — video/image uploads, likes, comments, bookmarks.

| File | What it does |
|------|-------------|
| `models.py` | `Post`, `Video`, `Image`, `Soundtrack`, `Like`, `Comment`, `Bookmark`, `CommentLike` |
| `views.py` | Upload, post detail, like/bookmark/comment (AJAX), conversations, activities |
| `forms.py` | `PostForm`, `VideoForm`, `ImageForm`, `SoundtrackForm`, `CommentForm` |
| `urls.py` | All `/post/` routes (upload, detail, like, comment, etc.) |
| `signals.py` | Deletes media files when a post is deleted; creates activity on like/comment |
| `admin.py` | Registers all post models in the admin panel |
| `management/` | Custom CLI command — `python manage.py load_soundtracks` |

---

### ⚙️ `tiktok/` — Project Configuration

The Django project root — connects everything together.

| File | What it does |
|------|-------------|
| `settings.py` | Database, static files, email config, installed apps, middleware |
| `urls.py` | Root URL router — sends traffic to `core/`, `post/`, and `admin/` |
| `wsgi.py` | Entry point for production deployment (WSGI servers) |
| `asgi.py` | Async entry point (ready for WebSockets / real-time features) |

---

### 🎨 `templates/` — HTML Pages & Components

All front-end templates organized by feature. Every page is server-side rendered with Django templates + Alpine.js for interactivity.

```
📁 templates/
├── 📁 components/          ← Reusable UI pieces
│   ├── sidebar.html           Navigation sidebar (collapsible)
│   ├── video_player.html      Video player wrapper
│   ├── video_grid.html        Thumbnail grid layout
│   ├── comments_panel.html    Comments overlay panel
│   ├── follow_button.html     Follow / unfollow button
│   ├── avatar.html            User avatar (image or initial fallback)
│   ├── navigation_dots.html   Scrolling dots for video feed
│   ├── more_panel.html        Settings & dark mode panel
│   ├── toast.html             Notification popup
│   └── empty_state.html       "Nothing here yet" placeholder
│
├── 📁 user/                ← Main app pages
│   ├── index.html             Landing / splash page
│   ├── login.html             Login form
│   ├── signup.html            Registration with email verification
│   ├── home.html              🎯 Main TikTok-style video feed
│   ├── explore.html           Search & browse
│   ├── profile.html           Your own profile page
│   ├── public_profile.html    Other user's profile page
│   ├── following.html         People you follow + suggestions
│   └── friends.html           Mutual follows' posts
│
├── 📁 post/                ← Post-related pages
│   ├── upload.html            Create a new post (drag & drop)
│   └── detail.html            Single post view with comments
│
└── 📁 emails/              ← HTML email templates
    └── verify_email.html      6-digit verification code email
```

---

### 🖼️ `static/` — CSS, JavaScript & Images

Front-end assets served directly to the browser.

```
📁 static/
├── 📁 src/
│   ├── input.css              Tailwind CSS source file
│   ├── output.css             🎨 Compiled Tailwind CSS (auto-built)
│   └── alpine.min.js          ⚡ Alpine.js library
├── 📁 images/
│   ├── logo.png               Browser tab icon (favicon)
│   └── robot.jpg
└── tiktok.png                 Logo used in the sidebar
```

---

### 📂 `media/` — User Uploads

Files uploaded by users (not tracked in git). Stored here during development.

```
📁 media/
├── 📁 user/
│   ├── 📁 videos/             🎥 Uploaded video files (.mp4)
│   └── 📁 profile_pictures/   🖼️ User avatar images
└── 📁 sound_tracks/           🎵 Audio files for soundtrack selection
```

---

### 📄 Root Files — Project Entry Points & Config

| File | Purpose |
|------|---------|
| `manage.py` | 🐍 Django CLI — runserver, migrate, createsuperuser, etc. |
| `package.json` | 📦 Node.js dependencies (Tailwind CSS CLI) |
| `requirements.txt` | 🐍 Python dependencies (Django, Pillow) |
| `README.md` | 📖 This file! |
| `screenshots/` | 🖼️ Add your page preview images here |

---

## Pages & Routes

### URL Map

| URL | Page | Description | Auth Required |
|---|---|---|---|
| `/` | Landing | Login/signup splash page | No |
| `/home/` | Home Feed | Main vertical video feed | Yes |
| `/login/` | Login | Sign in with email/username | No |
| `/signup/` | Signup | Register with email verification | No |
| `/logout/` | — | Log out and redirect to landing | Yes |
| `/profile/` | Profile | Your own profile page | Yes |
| `/following/` | Following | Users you follow + suggestions | Yes |
| `/explore/` | Explore | Search videos, users, hashtags | Yes |
| `/friends/` | Friends | Mutual follows' posts | Yes |
| `/post/upload/` | Upload | Create a new post | Yes |
| `/post/<id>/` | Post Detail | View single post | Yes |
| `/@<username>/` | Public Profile | View another user's profile | No |
| `/admin/` | Admin Panel | Django admin interface | Admin |

### API Endpoints (AJAX)

These endpoints return JSON responses for interactive features:

| Endpoint | Method | Purpose |
|---|---|---|
| `/follow/<username>/` | POST | Follow/unfollow a user |
| `/search/users/` | GET | Search users by query |
| `/post/<id>/like/` | POST | Toggle like on a post |
| `/post/<id>/bookmark/` | POST | Toggle bookmark on a post |
| `/post/<id>/comment/` | POST/GET | Add or list comments |
| `/post/comment/<id>/like/` | POST | Like a comment |
| `/post/comment/<id>/delete/` | POST | Delete a comment |
| `/post/conversations/` | GET | List conversations |
| `/post/activities/` | GET | List activity feed |

---

## Data Models

### Core App

| Model | Fields | Purpose |
|---|---|---|
| **EmailVerification** | `user`, `code` (6-digit), `created_at` | Stores email verification codes |
| **Profile** | `user`, `bio`, `profile_picture`, `followers` (M2M) | Extended user profile with social graph |
| **Activity** | `user` (recipient), `actor`, `activity_type`, `post`, `comment`, `text`, `created_at` | Notifications for likes, comments, follows, mentions |

### Post App

| Model | Fields | Purpose |
|---|---|---|
| **Post** | `user`, `video`, `image`, `soundtrack`, `caption`, `hashtags`, `privacy`, `scheduled_at`, `likes`, `comments`, `bookmarks`, `mentioned_users`, timestamps | Core content unit (video or image post) |
| **Video** | `file`, timestamps | Uploaded video file |
| **Image** | `file`, timestamps | Uploaded image file |
| **Soundtrack** | `title`, `artist`, `file`, timestamps | Audio tracks for posts |
| **Like** | `user`, `post` (unique together), timestamps | Post likes |
| **Comment** | `user`, `post`, `parent` (self-ref for replies), `text`, timestamps | Post comments with nesting |
| **CommentLike** | `user`, `comment` (unique together), timestamps | Comment likes |
| **Bookmark** | `user`, `post` (unique together), timestamps | Saved/bookmarked posts |

---

## Management Commands

Load audio files into the database as soundtracks:

```bash
python manage.py load_soundtracks
```

This looks for audio files in `media/sound_tracks/` and adds them to the database so users can select them when uploading posts. You can extend this command by editing `post/management/commands/load_soundtracks.py`.

---

## Customization Ideas

Here are some ways you can extend this project:

- **Replace SQLite with PostgreSQL** for production
- **Add WebSockets** for real-time notifications and chat
- **Implement video trimming/editing** before upload
- **Add image filters** using Pillow or a JS library
- **Deploy to production** using Docker, Railway, or Heroku
- **Add a recommendation algorithm** for the feed
- **Implement user blocking / reporting**
- **Add stories or live streaming**

---

## Contributing

Contributions are welcome! If you'd like to improve this project:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-idea`)
3. Commit your changes (`git commit -m 'Add amazing idea'`)
4. Push to the branch (`git push origin feature/amazing-idea`)
5. Open a Pull Request

Please make sure your code follows the existing style and includes appropriate tests.

---


<div align="center">

Created with ❤️ by [M Sami Shahid](https://github.com/msamishahid)

</div>
>>>>>>> changes
