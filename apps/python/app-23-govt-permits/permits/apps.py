import sys
from django.apps import AppConfig

class PermitsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'permits'

    def ready(self):
        # Only run migration/seeding when running a dev server or similar
        # (avoid run during test or check etc. if not needed, but runserver is standard)
        if 'runserver' in sys.argv or 'app' in sys.argv or 'manage.py' in sys.argv:
            try:
                from django.core.management import call_command
                # Create migrations and run migrate
                call_command('makemigrations', 'permits', interactive=False)
                call_command('migrate', interactive=False)

                from django.contrib.auth.models import User
                from .models import Permit

                # Seed users and permits if not already present
                if not User.objects.filter(username='citizen_john').exists():
                    john = User.objects.create_user(
                        username='citizen_john',
                        email='john@example.com',
                        password='john_pass_123'
                    )
                    jane = User.objects.create_user(
                        username='citizen_jane',
                        email='jane@example.com',
                        password='jane_pass_456'
                    )
                    # Staff user to act as reviewer
                    reviewer = User.objects.create_user(
                        username='reviewer_mark',
                        email='mark@govt.gov',
                        password='mark_pass_789',
                        is_staff=True
                    )

                    # Seed initial permit applications
                    Permit.objects.create(
                        title='Residential Building Permit',
                        applicant=john,
                        description='Application to construct a two-story residential house in Sector 4.'
                    )
                    Permit.objects.create(
                        title='Commercial Zone License',
                        applicant=jane,
                        description='Application to operate a retail coffee shop in Sector 7.'
                    )
            except Exception as e:
                # Suppress errors if DB isn't ready during imports or command lines
                pass
