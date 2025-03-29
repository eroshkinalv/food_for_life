from django import forms
from django.contrib.auth.forms import UserCreationForm

from rest_framework.exceptions import ValidationError

from users.models import CustomUser, StyleFormsMixin


class RegisterUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirmation = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")

        if password and password_confirmation and password != password_confirmation:
            raise forms.ValidationError("Пароли не совпадают.")

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "username",
            "avatar",
            "first_name",
            "phone_number",
            "password",
            "password_confirmation",
            "country",
        )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        first_name = cleaned_data.get("first_name")

        if username.lower() and first_name.lower() in [
            "казино",
            "криптовалюта",
            "крипта",
            "биржа",
            "дешево",
            "бесплатно",
            "обман",
            "полиция",
            "радар",
        ]:
            self.add_error("username", "запрещенное слово")
            self.add_error("first_name", "запрещенное слово")

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError("Номер телефона должен состоять только из цифр")
        return phone_number

    def clean_avatar(self):
        cleaned_data = super().clean()
        avatar = cleaned_data.get("image")

        if avatar is None:
            return None

        if avatar.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Размер файла не должен превышать 5MB.")

        if not avatar.name.endswith(("jpg", "jpeg", "png")):
            raise forms.ValidationError(
                "Формат файла не соответствует требованиям. " "Формат файла должен быть *.jpg, *.jpeg, *.png"
            )

        return avatar


class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "email",
            "username",
            "avatar",
            "first_name",
            "phone_number",
            "country",
        ]
        exclude = (
            "is_blocked",
            "owner",
        )


class UserRegisterForm(StyleFormsMixin, forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = (
            "email",
            "username",
            "avatar",
            "first_name",
            "phone_number",
            "password1",
            "password2",
            "country",
        )

    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):

        super(UserRegisterForm, self).__init__(*args, **kwargs)

        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Придумайте пароль",
            }
        )

        self.fields["password1"].label = "Пароль"
        self.fields["password1"].help_text = (
            "Пароль должен состоять не менее, чем из 8 символов. "
            "Пароль не должен включать в себя легко вычисляемые сочетания символов."
        )

        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Повторите пароль",
            }
        )

        self.fields["password2"].label = "Подтверждение пароля"
        self.fields["password2"].help_text = ""

        self.fields["email"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Введите адрес электронной почты",
            }
        )


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = "__all__"
        exclude = ("password",)

    def __init__(self, *args, **kwargs):

        super(UserUpdateForm, self).__init__(*args, **kwargs)

        self.fields["image"].widget.attrs.update(
            {
                "placeholder": "",
            }
        )

        self.fields["image"].help_text = ""
        self.fields["image"].label = "Your name"
        self.fields["image"].localized_field = "Your name"
        self.fields["image"].fieldset = "Your name"
        self.fields["image"].initial = "Your name"

        self.fields["phone"].widget.attrs.update(
            {
                "placeholder": "Укажите телефон",
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

        if image_size > max_size:
            raise ValidationError("Размер файла не должен превышать 5МБ")

        elif not (image_name.endswith("png") or image_name.endswith("jpg")):
            raise ValidationError("Формат файла должен быть PNG или JPEG")

        return image


class PasswordUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("email",)

    def __init__(self, *args, **kwargs):

        super(PasswordUpdateForm, self).__init__(*args, **kwargs)

        self.fields["email"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Введите адрес электронной почты",
            }
        )


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
