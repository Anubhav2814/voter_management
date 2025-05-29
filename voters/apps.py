from django.apps import AppConfig

class VotersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'voters'

    def ready(self):
        """
        Ensures that the app is ready to use custom template tags.
        """
        try:
            import voters.templatetags.voter_extras  # Import the template tags
        except ImportError:
            pass