# Generated by Django 5.1.7 on 2025-03-28 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Reservation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(help_text="Введите имя", max_length=100, verbose_name="Имя пользователя")),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(max_length=15)),
                ("date", models.DateField()),
                ("time", models.TimeField(verbose_name="Время бронирования")),
                ("guests", models.IntegerField()),
                ("created_at", models.DateTimeField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("Сonfirm", "Подтверждено"), ("Reserved", "В ожидании"), ("Canceled", "Отменено")],
                        default="Reserved",
                        max_length=20,
                    ),
                ),
            ],
            options={
                "verbose_name": "Резервирование",
                "verbose_name_plural": "Резервирования",
                "ordering": ["guests", "date"],
                "permissions": [
                    ("can_view_all_reservation", "can view all reservation"),
                    ("can_view_reservations", "Can view reservations"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Tables",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.CharField(default=1, max_length=10, verbose_name="Номер стола")),
                (
                    "status",
                    models.CharField(
                        choices=[("available", "Свободен"), ("reserved", "Зарезервирован")],
                        default="available",
                        max_length=10,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "capacity",
                    models.IntegerField(
                        default=1, help_text="Введите максимальное количество гостей", verbose_name="Вместимость"
                    ),
                ),
            ],
            options={
                "verbose_name": "Стол",
                "verbose_name_plural": "Столы",
                "ordering": ["status", "number"],
            },
        ),
    ]
