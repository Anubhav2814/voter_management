from django.apps import AppConfig

class VotersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'voters'

    def ready(self):
        try:
            import voters.templatetags.voter_extras  # Import the template tags
        except ImportError:
            pass