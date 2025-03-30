from django.db import models

from users.models import CustomUser


class Tables(models.Model):
    """Модель столов"""

    STATUS_CHOICES = [
        ("available", "Свободен"),
        ("reserved", "Зарезервирован"),
    ]

    number = models.CharField(default=1, max_length=10, verbose_name="Номер стола")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="available", verbose_name="Статус")
    capacity = models.IntegerField(
        default=1, verbose_name="Вместимость", help_text="Введите максимальное количество гостей"
    )

    def __str__(self):
        return f"Стол {self.number} - {self.get_status_display()} (вместимость: {self.capacity})"

    class Meta:
        verbose_name = "Стол"
        verbose_name_plural = "Столы"
        ordering = ["status", "number"]


class Reservation(models.Model):
    """Модель бронирования"""

    STATUS_CHOICES = [
        ("Сonfirm", "Подтверждено"),
        ("Reserved", "В ожидании"),
        ("Canceled", "Отменено"),
    ]

    owner = models.ForeignKey(
        CustomUser,
        verbose_name="Владелец",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    name = models.CharField(max_length=100, verbose_name="Имя пользователя")
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    date = models.DateField()
    time = models.TimeField(verbose_name="Время бронирования")
    guests = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    table = models.ForeignKey(Tables, on_delete=models.CASCADE, verbose_name="Стол", related_name="reservations")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Reserved")

    def __str__(self):
        return f"Бронирование от {self.name} на {self.date} в {self.time} на {self.guests} гостей"

    def is_table_available(self):
        return not Reservation.objects.filter(table=self.table, date=self.date, time=self.time).exists()

    class Meta:
        verbose_name = "Резервирование"
        verbose_name_plural = "Резервирования"
        ordering = ["guests", "date"]
        permissions = [
            ("can_view_all_reservation", "can view all reservation"),
            ("can_view_reservations", "Can view reservations"),
        ]


class Contact(models.Model):

    name = models.CharField(max_length=150, verbose_name="Имя")
    phone = models.CharField(max_length=12, null=True, blank=True, verbose_name="Телефон")
    message = models.TextField(null=True, blank=True, verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.p_name} ({self.phone}): {self.message} / {self.created_at}"

    class Meta:
        verbose_name = "Обратная связь"
        verbose_name_plural = "Обратная связь"
        ordering = ["created_at"]


class Services(models.Model):

    service_name = models.CharField(max_length=150, null=True, blank=True, verbose_name="Название услуги")
    service_detail = models.TextField(null=True, blank=True, verbose_name="Описание услуги")

    image = models.ImageField(upload_to="service_img/", verbose_name="Изображение", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Сервис"
        verbose_name_plural = "Сервисы"

    def __str__(self):
        return self.service_name


class Restaurant(models.Model):

    name = models.CharField(max_length=200, null=True, blank=True, verbose_name="Название ресторана")

    slogan = models.CharField(max_length=200, null=True, blank=True, verbose_name="Слоган ресторана")

    description = models.TextField(
        verbose_name="Описание ресторана",
        blank=True,
        null=True,
    )

    background = models.TextField(verbose_name="История ресторана", blank=True, null=True)
    mission_and_values = models.TextField(verbose_name="Миссия и ценности", blank=True, null=True)

    image_description = models.ImageField(upload_to="interior/", verbose_name="Фото ресторана", blank=True, null=True)
    image_service = models.ImageField(upload_to="interior/", verbose_name="Фото услуг", blank=True, null=True)
    image_background = models.ImageField(upload_to="interior/", verbose_name="Фото услуг", blank=True, null=True)
    image_mission_and_values = models.ImageField(
        upload_to="interior/", verbose_name="Фото для миссии", blank=True, null=True
    )

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        verbose_name = "Ресторан"
        verbose_name_plural = "Рестораны"

    def __str__(self):
        return self.name


class Employees(models.Model):

    first_name = models.CharField(verbose_name="Имя сотрудника", help_text="Введите имя")
    last_name = models.CharField(verbose_name="Фамилия сотрудника", help_text="Введите фамилию")
    position = models.CharField(verbose_name="Должность сотрудника", help_text="Введите дложность")
    image = models.ImageField(upload_to="employees/", verbose_name="Фото сотрудника", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.position}"


class Menu(models.Model):

    item_food = models.CharField(max_length=150, null=True, blank=True, verbose_name="Блюдо")
    item_drink = models.CharField(max_length=150, null=True, blank=True, verbose_name="Напиток")

    price = models.IntegerField(null=True, blank=True, verbose_name="Цена блюда")
    image = models.ImageField(upload_to="menu_images/", verbose_name="Фото блюда")
    size = models.IntegerField(null=True, blank=True, verbose_name="Размер порции (в гр.)")
    kcal = models.IntegerField(null=True, blank=True, verbose_name="Калорийность")
    if_vegan = models.BooleanField(default=False, verbose_name="Вегетерианское блюдо")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Меню"
        verbose_name_plural = "Меню"
        ordering = ["created_at"]
