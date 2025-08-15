from datetime import timedelta, datetime
from django.core.exceptions import ValidationError
from django import forms
from restaurant.models import Reservation, Tables, Contact, Restaurant, Services, Employees, Menu
from django.forms import BooleanField, DateTimeInput
from django.db.models import Q

BANNED_WORDS = ["казино", "криптовалюта", "крипта", "биржа", "дешево", "бесплатно", "обман", "полиция", "радар"]


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fild_name, fild in self.fields.items():
            if isinstance(fild, BooleanField):
                fild.widget.attrs["class"] = "form-check-input"
            else:
                fild.widget.attrs["class"] = "form-control"


class ReservationForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            "table",
            "name",
            "email",
            "phone",
            "date",
            "time",
            "guests",
        ]
        widgets = {
            "date": DateTimeInput(attrs={"type": "date"}),
            "time": DateTimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super(ReservationForm, self).__init__(*args, **kwargs)
        self.fields["guests"].widget.attrs.update(
            {
                "class": "form-control",  # Добавление CSS-класса для стилизации поля
                "placeholder": "Введите количество гостей",
            }
        )

        self.fields["phone"].label = "Телефон"
        self.fields["date"].label = "Дата"
        self.fields["guests"].label = "Количество гостей"
        self.fields["table"].label = "Список столов. Выберите свободный"  # Изменяем название поля
        self.fields["table"].widget.attrs.update(
            {
                "class": "form-control",  # Добавление CSS-класса для стилизации поля
            }
        )

    def clean(self):
        """Валидация формы, на проверку отсутствия брони выбранного столика."""
        cleaned_data = super().clean()
        table = cleaned_data.get("table")
        date = cleaned_data.get("date")
        time = cleaned_data.get("time")

        if date and time:
            reserved_at = datetime.combine(date, time)
            current_time = datetime.now()

            # Проверяем, что дата и время не в прошлом
            if reserved_at < current_time:
                raise ValidationError("Вы не можете забронировать столик на прошедшую дату и время.")

            start_time = reserved_at
            end_time = reserved_at + timedelta(minutes=60)

            # Проверяем, есть ли текущее бронирование на этот столик
            if Reservation.objects.filter(
                Q(table=table)
                & Q(date=date)
                & Q(time__lt=end_time.time())  # Проверяем, что время меньше конца нового бронирования
                & Q(time__gte=start_time.time())  # Проверяем, что время больше или равно началу нового бронирования
            ).exists():
                raise ValidationError(
                    f"Выбранный столик №{table.number} уже забронирован в это время, "
                    f"пожалуйста выберите другое время."
                )

            # Дополнительно, проверяем, что новое бронирование не начинается в течение часа после предыдущего
            # Получаем все предыдущие бронирования
            previous_reservations = Reservation.objects.filter(
                Q(table=table)
                & Q(date=date)
                & Q(time__lt=start_time.time())  # Предыдущие бронирования, заканчивающиеся до начала нового
            )

            # Проверяем, есть ли бронирования, которые заканчиваются позже, чем через час до нового бронирования
            for reservation in previous_reservations:
                reservation_end_time = datetime.combine(reservation.date, reservation.time) + timedelta(minutes=60)
                if reservation_end_time > start_time:
                    raise ValidationError(
                        f"Выбранный столик №{table.number} не может быть забронирован в течение часа "
                        f"после предыдущей брони."
                    )
        return cleaned_data

    def save(self, commit=True):
        """Сохранение успешного бронирования."""
        reservation = super().save(commit=False)

        if commit:
            reservation.save()  # Сохраняем в БД
        return reservation
        # self.fields['table'].queryset = Tables.objects.filter(status="available")


class ContactForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["name", "phone", "message"]

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {
                "class": "form-control",  # Добавление CSS-класса для стилизации поля
                "placeholder": "Укажите имя",
            }
        )
        self.fields["phone"].widget.attrs.update(
            {
                "class": "form-control",  # Добавление CSS-класса для стилизации поля
                "placeholder": "Укажите телефон",
            }
        )
        self.fields["message"].widget.attrs.update(
            {
                "class": "form-control",  # Добавление CSS-класса для стилизации поля
                "placeholder": "Напишите сообщение",
            }
        )


class RestaurantForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = "__all__"

    def __init__(self, *args, **kwargs):

        super(RestaurantForm, self).__init__(*args, **kwargs)

        self.fields["name"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Введите название ресторана",
            }
        )

        self.fields["description"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Опишите Ваш ресторан",
            }
        )

        self.fields["background"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Опишите историю Вашего ресторана",
            }
        )

        self.fields["mission_and_values"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Опишите миссию и цености ресторана",
            }
        )

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def clean_description(self):

        description = self.cleaned_data.get("description")

        for word in description.split():
            if word.lower() in BANNED_WORDS:
                self.add_error("description", f'Описание не может содержать слово "{word}".')
            return description

    def clean_image(self):

        image = self.cleaned_data.get("image")
        image_size = image.size
        image_name = image.name
        max_size = 5 * 1024 * 1024

        if image:
            if image_size > max_size:
                raise ValidationError("Размер файла не должен превышать 5МБ")

            elif not (image_name.endswith("png") or image_name.endswith("jpg")):
                raise ValidationError("Формат файла должен быть PNG или JPEG")

        return image


class RestaurantServiceForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Services
        fields = "__all__"

    def __init__(self, *args, **kwargs):

        super(RestaurantServiceForm, self).__init__(*args, **kwargs)

        self.fields["service_name"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Введите название услуги",
            }
        )

        self.fields["service_detail"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Введите описание услуги",
            }
        )

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def clean_image(self):

        image = self.cleaned_data.get("image")
        if image:
            image_size = image.size
            image_name = image.name
            max_size = 5 * 1024 * 1024

            if image_size > max_size:
                raise ValidationError("Размер файла не должен превышать 5МБ")

            elif not (image_name.endswith("png") or image_name.endswith("jpg")):
                raise ValidationError("Формат файла должен быть PNG или JPEG")

        return image


class EmployeeForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Employees
        exclude = ("created_at",)

    def __init__(self, *args, **kwargs):

        super(EmployeeForm, self).__init__(*args, **kwargs)

        self.fields["first_name"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Имя сотрудника",
            }
        )

        self.fields["last_name"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Фамилия сотрудника",
            }
        )

        self.fields["position"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Должность сотрудника",
            }
        )

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def clean_image(self):

        image = self.cleaned_data.get("image")
        image_size = image.size
        image_name = image.name
        max_size = 5 * 1024 * 1024

        if image:
            if image_size > max_size:
                raise ValidationError("Размер файла не должен превышать 5МБ")

            elif not (image_name.endswith("png") or image_name.endswith("jpg")):
                raise ValidationError("Формат файла должен быть PNG или JPEG")

        return image


class TableForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Tables
        exclude = ("status",)

    def __init__(self, *args, **kwargs):

        super(TableForm, self).__init__(*args, **kwargs)


class MenuForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Menu
        fields = "__all__"

    def __init__(self, *args, **kwargs):

        super(MenuForm, self).__init__(*args, **kwargs)
