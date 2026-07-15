from django import forms
from .models import Post, Video, Image, Soundtrack, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['caption', 'hashtags']
        widgets = {
            'caption': forms.Textarea(attrs={
                'rows': 4, 'class': 'w-full bg-neutral-100 dark:bg-neutral-800 border border-neutral-300 dark:border-neutral-600 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-neutral-500 dark:focus:border-neutral-400 dark:text-white dark:placeholder-neutral-400 resize-none', 'placeholder': 'Describe your video'
            }),
            'hashtags': forms.TextInput(attrs={
                'class': 'w-full bg-neutral-100 dark:bg-neutral-800 border border-neutral-300 dark:border-neutral-600 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-neutral-500 dark:focus:border-neutral-400 dark:text-white dark:placeholder-neutral-400', 'placeholder': 'Hashtags (e.g. #romantic #couple)'
            }),
        }


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'accept': 'video/*', 'class': 'hidden'}),
        }


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'accept': 'image/*', 'class': 'hidden'}),
        }


class SoundtrackForm(forms.ModelForm):
    class Meta:
        model = Soundtrack
        fields = ['title', 'artist', 'file']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 2, 'class': 'w-full bg-neutral-100 dark:bg-neutral-800 border border-neutral-300 dark:border-neutral-600 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-neutral-500 dark:focus:border-neutral-400 dark:text-white dark:placeholder-neutral-400 resize-none', 'placeholder': 'Add a comment...'
            }),
        }
