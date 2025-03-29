import os
import random
import secrets

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView

from restaurant.models import Reservation
from users.forms import RegisterUserCreationForm, UserRegisterForm, UserUpdateForm, PasswordUpdateForm
from users.models import CustomUser


class RegisterView(CreateView):
    """Представление регистрации пользователя"""

    form_class = RegisterUserCreationForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save(commit=False)  # Не сохраняем в БД сразу
        user.is_active = False
        user.set_password(form.cleaned_data["password"])
        user = form.save()
        login(self.request, user)
        self.send_welcome_email(user.email)
        return super().form_valid(form)

    def send_welcome_email(self, user_email):
        subject = "Добро пожаловать в наш сервис"
        activation_link = f"http://127.0.0.1:8000/users/confirm-email/{user_email}/"
        message = (
            f"Спасибо, что зарегистрировались в нашем сервисе!\n\n "
            f"Пожалуйста, подтвердите ваш адрес электронной почты, перейдя по следующей ссылке:\n "
            f"{activation_link}\n\n "
            f"Мы рады видеть вас среди наших пользователей."
        )
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user_email]
        send_mail(subject, message, from_email, recipient_list)


class ConfirmEmailView(View):
    """Представление подтверждения почты"""

    def get(self, request, user_email):
        user = get_object_or_404(CustomUser, email=user_email)
        activation_link = f"http://127.0.0.1:8000/users/login/"
        if user.is_active:
            return HttpResponse("Ваш адрес электронной почты уже подтвержден!")

        user.is_active = True
        user.save()
        messages.success(request, "Ваш адрес электронной почты был успешно подтвержден! Вы можете войти.")
        return HttpResponseRedirect(reverse("users:login"))


class UserDetailView(DetailView):
    """Представление детальной информации о пользователе"""

    model = CustomUser
    template_name = "users/user_profile.html"
    context_object_name = "user_profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        reservations = Reservation.objects.filter(owner=user)
        context["reservations"] = reservations

        print(f":User  {user.username}, Reservations Count: {reservations.count()}")

        return context


class BlockUserView(LoginRequiredMixin, View):
    """Представление блокировки пользователя"""

    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        return render(request, "users/user_block.html", {"user": user})

    def post(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)

        if not request.user.has_perm("users.can_block_users"):
            return HttpResponseForbidden("У вас нет прав для блокировки рассылки.")

        is_blocked = request.POST.get("is_blocked")
        user.is_blocked = is_blocked == "on"
        user.save()
        return redirect("users:user_list")


class UserCreateView(CreateView):
    model = CustomUser
    form_class = UserRegisterForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("users:login")
    context_object_name = "users"

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(5)
        user.token = token
        user.save()
        url = f"http://{self.request.get_host()}/users/email_confirm/{token}/"

        send_mail(
            "Подтверждение адреса электронной почты",
            f"Подтвердите регистацию на сайте. Перейдите по ссылке: {url} .",
            os.getenv("EMAIL_HOST_USER"),
            [f"{user.email}"],
            fail_silently=False,
        )

        return super().form_valid(form)


class UserUpdateView(UpdateView):
    model = CustomUser
    form_class = UserUpdateForm
    template_name = "users/user_update_form.html"
    success_url = reverse_lazy("restaurant:home")


class UserListView(ListView):
    model = CustomUser
    form_class = UserRegisterForm
    template_name = "users/user_list.html"
    context_object_name = "user_list"

    def get_queryset(self):
        return CustomUser.objects.all()

    def get_context_data(self, **kwargs):

        user = self.request.user
        context = super(UserListView, self).get_context_data(**kwargs)

        if user.has_perm("managers"):
            context["status"] = "Менеджер"
            return context

        context["status"] = "Пользователь"
        return context


def email_verification(request, token):
    user = get_object_or_404(CustomUser, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse("users:login"))


class PasswordTemplateView(TemplateView):

    form_class = PasswordUpdateForm
    template_name = "users/password_form.html"
    success_url = reverse_lazy("users:login")

    def post(self, request):

        if request.method == "POST":
            email = request.POST.get("email")
            user = CustomUser.objects.filter(email=email).first()
            if user:

                password = str(random.randint(10000000, 99999999))
                user.set_password(password)
                user.save()

                send_mail(
                    "Смена пароля",
                    f"Ваш новый пароль: {password} .",
                    os.getenv("EMAIL_HOST_USER"),
                    [f"{email}"],
                    fail_silently=False,
                )

        return render(request, "users/login.html")

    def get_context_data(self, **kwargs):

        context = super(PasswordTemplateView, self).get_context_data(**kwargs)
        context["form"] = PasswordUpdateForm()

        return context
