from django.apps import AppConfig


class OgrencilerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ogrenciler'
    verbose_name = 'Öğrenciler'
    
    def ready(self):
        import ogrenciler.signals  # Signal'ları import et
