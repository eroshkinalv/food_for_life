from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.views.generic import TemplateView, CreateView
from django.views.generic import View
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib import messages
from django.views.generic import FormView, DeleteView, UpdateView, ListView, DetailView
from django.urls import reverse_lazy
from .forms import (
    ReservationForm,
    ContactForm,
    RestaurantForm,
    RestaurantServiceForm,
    TableForm,
    EmployeeForm,
    MenuForm,
)
from .models import Tables, Reservation, Contact, Restaurant, Services, Employees, Menu
from django.contrib.auth.mixins import LoginRequiredMixin


class HomePageView(View):
    """Представление главной страницы"""

    template_name = "restaurant/home.html"

    def get(self, request):
        return render(request, self.template_name)


class HomePageListView(ListView):
    """Представление главной страницы"""

    model = Contact
    template_name = "restaurant/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = {
            "restaurant": Restaurant.objects.all(),
            "service_choice": Services.objects.all(),
            "tables": Tables.objects.all(),
            "employees": Employees.objects.all(),
            "menu": Menu.objects.all(),
            "form": ContactForm,
        }
        context.update(data)
        return context


class AboutRestaurantView(TemplateView):
    """Представление страницы о ресторане"""

    template_name = "restaurant/about_restaurant.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = {
            "restaurant": Restaurant.objects.all(),
            "service_choice": Services.objects.all(),
            "tables": Tables.objects.all(),
            "employees": Employees.objects.all(),
            "menu": Menu.objects.all(),
            "form": ContactForm,
        }
        context.update(data)
        return context


class ReservationListView(LoginRequiredMixin, ListView):
    """Представление списка всех бронирований"""

    model = Reservation
    form_class = ReservationForm
    template_name = "restaurant/reservation_list.html"
    context_object_name = "reservation_list"

    def get_queryset(self):
        # Здесь вы можете определить свой queryset
        return Reservation.objects.all()


class ReservationDetailView(LoginRequiredMixin, DetailView):
    """Представление детальной информации о бронировании"""

    model = Reservation
    template_name = "restaurant/reservation_detail.html"
    context_object_name = "reservation_detail"

    def get(self, request, id):
        reservation = get_object_or_404(Reservation, id=id)
        return render(request, "restaurant/reservation_detail.html", {"reservation": reservation})


class ReservationView(FormView):
    """Представление бронирования стола"""

    template_name = "restaurant/reservation.html"
    form_class = ReservationForm

    def form_valid(self, form):
        table = form.cleaned_data["table"]
        date = form.cleaned_data["date"]
        time = form.cleaned_data["time"]
        guests = form.cleaned_data["guests"]

        # Создаем объект Reservation для проверки доступности стола
        reservation = Reservation(
            table=table,
            date=date,
            time=time,
            guests=guests,
            name=form.cleaned_data["name"],
            email=form.cleaned_data["email"],
            phone=form.cleaned_data["phone"],
        )

        # Проверяем доступность стола
        if not reservation.is_table_available():
            messages.error(
                self.request,
                "К сожалению, этот стол уже забронирован на выбранное время. "
                "Пожалуйста, выберите другой стол или время.",
            )
            return self.form_invalid(form)

        if guests > table.capacity:
            messages.error(
                self.request, f"Количество гостей не должно превышать вместимость " f"стола: {table.capacity}."
            )
            return self.form_invalid(form)

        try:
            reservation.owner = self.request.user  # Привязываем текущего пользователя как владельца
            reservation.save()  # Сохраняем в БД
            messages.success(self.request, "Ваша бронь успешно создана!")
            return redirect("restaurant:confirm_reservation", reservation_id=reservation.id)
        except ValidationError as e:
            messages.error(self.request, "Ошибка: " + str(e))
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Произошла ошибка с вашей бронью. Пожалуйста, исправьте ошибки ниже.")
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["available_tables"] = Tables.objects.filter(status="available")
        context["all_tables"] = Tables.objects.all()  # Добавляем все столы
        context["restaurant"] = Restaurant.objects.all()

        return context


class ConfirmReservationView(TemplateView):
    """Представление подтверждения бронирования"""

    template_name = "restaurant/confirm_reservation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reservation_id = self.kwargs.get("reservation_id")

        try:
            context["reservation_data"] = Reservation.objects.get(id=reservation_id)
        except Reservation.DoesNotExist:
            context["reservation_data"] = None

        return context

    def post(self, request, *args, **kwargs):
        reservation_id = self.kwargs.get("reservation_id")
        try:
            reservation = Reservation.objects.get(id=reservation_id)
            reservation.status = "confirmed"

            # Проверяем доступность стола перед сохранением
            if not reservation.is_table_available():
                messages.error(request, "Стол уже забронирован на это время.")
                return redirect("restaurant:home")

            reservation.save()
            messages.success(request, "Ваше бронирование подтверждено!")
            return redirect("restaurant:home")
        except Reservation.DoesNotExist:
            messages.error(request, "Бронирование не найдено.")
            return redirect("restaurant:home")


class CancelReservationView(LoginRequiredMixin, DeleteView):
    """Представление отмены брони"""

    model = Reservation
    template_name = "restaurant/confirm_reservation_delete.html"  # Укажите путь к вашему шаблону, если нужен

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.user.has_perm("restaurant:delete_reservation")
            or self.request.reservation.owner
        )

    def handle_no_permission(self):
        return redirect("restaurant:delete_reservation")

    def get_object(self, queryset=None):
        # Получите объект по первичному ключу (pk)
        return super().get_object(queryset)

    def get_success_url(self):
        # Используйте правильное имя поля owner
        user_id = self.object.owner.id if self.object.owner else None  # Проверяем, есть ли владелец
        self.object.table.status = "available"
        self.object.table.save()
        return (
            reverse_lazy("users:user_profile", kwargs={"pk": user_id})
            if user_id
            else reverse_lazy("default_redirect_url")
        )


class ReservationDeleteView(LoginRequiredMixin, DeleteView):

    model = Reservation
    template_name = "restaurant/reservation_delete.html"  # Убедитесь, что этот шаблон существует
    success_url = reverse_lazy("restaurant:reservation_list")

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.has_perm("restaurant:delete_reservation")

    def get_object(self, queryset=None):
        # Получите объект по первичному ключу (pk)
        return super().get_object(queryset)


class ReservationUpdateView(LoginRequiredMixin, UpdateView):
    """Представление редактирование бронирования"""

    model = Reservation
    form_class = ReservationForm
    template_name = "restaurant/reservation.html"
    success_url = reverse_lazy("users:user_profile")

    def form_valid(self, form):
        try:
            form.save()
            return super().form_valid(form)
        except ValidationError as e:
            form.add_error(None, e)  # Добавляем ошибку в форму
            return self.form_invalid(form)


class ContactsView(View):
    """Представление контактов и обратной связи"""

    @staticmethod
    def get(request):
        return render(request, "restaurant/contacts.html")

    @staticmethod
    def post(request):
        name = request.POST.get("name")
        massage = request.POST.get("massage")
        return HttpResponse(f"Спасибо, {name}. Сообщение получено.")


class UpdateReservationStatusView(View):
    def post(self, request, reservation_id):
        reservation = get_object_or_404(Reservation, id=reservation_id)
        new_status = request.POST.get("status")

        # Получаем список доступных статусов
        valid_statuses = [status[0] for status in Reservation.STATUS_CHOICES]

        if new_status in valid_statuses:
            # Если статус "Сonfirm", необходимо убедиться, что он может быть установлен
            if new_status == "Сonfirm" and reservation.status != "Reserved":
                return HttpResponseBadRequest("Статус может быть изменен на 'Подтверждено' только из 'В ожидании'.")

        if new_status in valid_statuses:
            reservation.status = new_status
            reservation.save()

        return redirect("restaurant:reservation_list")


class ContactsCreateView(CreateView):
    """Представление для создания формы обратной связи"""

    model = Contact
    form_class = ContactForm
    template_name = "restaurant/contacts_create.html"
    success_url = reverse_lazy("restaurant:home")


class ChangesView(TemplateView):
    """Представление для редактирования данных о ресторане"""

    template_name = "restaurant/changes.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = {
            "restaurant": Restaurant.objects.all(),
            "service_choice": Services.objects.all(),
            "tables": Tables.objects.all(),
            "employees": Employees.objects.all(),
            "menu": Menu.objects.all(),
        }
        context.update(data)
        return context


class RestaurantCreateView(CreateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = "restaurant/home_form.html"
    success_url = reverse_lazy("restaurant:home")
    context_object_name = "restaurant"


class RestaurantUpdateView(UpdateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = "restaurant/home_form.html"
    success_url = reverse_lazy("restaurant:home")


class RestaurantDeleteView(DeleteView):
    model = Restaurant
    success_url = reverse_lazy("restaurant:home")


class RestaurantDetailView(DetailView):
    model = Restaurant
    template_name = "restaurant/home.html"
    context_object_name = "restaurant"


class ServicesCreateView(CreateView):
    model = Services
    form_class = RestaurantServiceForm
    template_name = "restaurant/service_form.html"
    success_url = reverse_lazy("restaurant:service_list")


class ServicesUpdateView(UpdateView):
    model = Services
    form_class = RestaurantServiceForm
    template_name = "restaurant/service_form.html"
    success_url = reverse_lazy("restaurant:service_list")


class ServicesListView(ListView):
    model = Services
    template_name = "restaurant/service.html"
    context_object_name = "services"

    def get_context_data(self, **kwargs):

        context = super(ServicesListView, self).get_context_data(**kwargs)
        context["form"] = RestaurantServiceForm()

        return context


class ServicesDeleteView(DeleteView):
    model = Services
    success_url = reverse_lazy("restaurant:home")


class ServicesDetailView(DetailView):
    model = Services
    template_name = "restaurant/service_view.html"
    context_object_name = "service"


class TablesCreateView(CreateView):
    model = Tables
    form_class = TableForm
    template_name = "restaurant/tables_form.html"
    success_url = reverse_lazy("restaurant:tables_list")


class TablesUpdateView(UpdateView):
    model = Restaurant
    form_class = TableForm
    template_name = "restaurant/tables_form.html"
    success_url = reverse_lazy("restaurant:tables_list")


class TablesListView(ListView):
    model = Tables
    template_name = "restaurant/tables.html"
    context_object_name = "tables"

    def get_context_data(self, **kwargs):

        context = super(TablesListView, self).get_context_data(**kwargs)
        context["form"] = TableForm()

        return context


class TablesDeleteView(DeleteView):
    model = Tables
    success_url = reverse_lazy("restaurant:home")


class TablesDetailView(DetailView):
    model = Tables
    template_name = "restaurant/tables_view.html"
    context_object_name = "table"


class EmployeesCreateView(CreateView):
    model = Employees
    form_class = EmployeeForm
    template_name = "restaurant/employee_form.html"
    success_url = reverse_lazy("restaurant:employees_list")


class EmployeesUpdateView(UpdateView):
    model = Employees
    form_class = EmployeeForm
    template_name = "restaurant/employee_form.html"
    success_url = reverse_lazy("restaurant:employees_list")


class EmployeesListView(ListView):
    model = Employees
    template_name = "restaurant/employees.html"
    context_object_name = "employees"

    def get_context_data(self, **kwargs):

        context = super(EmployeesListView, self).get_context_data(**kwargs)
        context["form"] = EmployeeForm()

        return context


class EmployeesDeleteView(DeleteView):
    model = Employees
    success_url = reverse_lazy("restaurant:home")


class EmployeesDetailView(DetailView):
    model = Employees
    template_name = "restaurant/employees_view.html"
    context_object_name = "employee"


class MenuCreateView(CreateView):
    model = Menu
    form_class = MenuForm
    template_name = "restaurant/menu_form.html"
    success_url = reverse_lazy("restaurant:menu_list")


class MenuUpdateView(UpdateView):
    model = Menu
    form_class = MenuForm
    template_name = "restaurant/menu_form.html"
    success_url = reverse_lazy("restaurant:menu_list")


class MenuListView(ListView):
    model = Menu
    template_name = "restaurant/menu.html"
    context_object_name = "menu"

    def get_context_data(self, **kwargs):

        context = super(MenuListView, self).get_context_data(**kwargs)
        context["form"] = MenuForm()

        return context


class MenuDeleteView(DeleteView):
    model = Menu
    success_url = reverse_lazy("restaurant:home")


class MenuDetailView(DetailView):
    model = Menu
    template_name = "restaurant/menu_view.html"
    context_object_name = "menu"
