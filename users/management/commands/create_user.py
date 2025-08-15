from django.core.management.base import BaseCommand
from users.models import CustomUser


class Command(BaseCommand):
    help = "Добавьте пользователя"

    def handle(self, *args, **kwargs):

        user = CustomUser.objects.create(email="admin@example.com")

        user.set_password("123zaq")
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
