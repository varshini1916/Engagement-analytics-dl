from django.core.management.base import BaseCommand
from accounts.models import CustomUser, Profile

class Command(BaseCommand):
    help = 'Create missing profiles for users who do not have one'

    def handle(self, *args, **kwargs):
        users_without_profile = CustomUser.objects.filter(profile__isnull=True)
        count = 0
        for user in users_without_profile:
            Profile.objects.create(user=user)
            count += 1
            self.stdout.write(f'Created profile for user: {user.username}')
        self.stdout.write(self.style.SUCCESS(f'Total profiles created: {count}'))
