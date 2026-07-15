import os
from django.core.management.base import BaseCommand
from django.conf import settings
from post.models import Soundtrack


class Command(BaseCommand):
    help = 'Load audio files from media/sound_tracks/ into the Soundtrack table'

    def handle(self, *args, **options):
        folder = os.path.join(settings.MEDIA_ROOT, 'sound_tracks')
        if not os.path.exists(folder):
            self.stdout.write(self.style.ERROR(f'Folder not found: {folder}'))
            return

        audio_extensions = {'.mp3', '.wav', '.ogg', '.aac', '.flac', '.m4a', '.wma'}
        loaded = 0

        for fname in os.listdir(folder):
            ext = os.path.splitext(fname)[1].lower()
            if ext not in audio_extensions:
                continue

            title = os.path.splitext(fname)[0]
            rel_path = os.path.join('sound_tracks', fname)

            obj, created = Soundtrack.objects.get_or_create(
                title=title,
                defaults={'file': rel_path}
            )
            if created:
                loaded += 1
                self.stdout.write(self.style.SUCCESS(f'  Loaded: {title}'))
            else:
                obj.file = rel_path
                obj.save()

        self.stdout.write(self.style.SUCCESS(f'Done. {loaded} soundtrack(s) loaded.'))
