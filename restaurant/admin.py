from django.contrib import admin
from restaurant.models import Reservation, Tables, Restaurant, Services, Employees


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "guests", "owner")
    list_filter = ("is_active", "date")
    search_fields = ("user__username",)


@admin.register(Tables)
class TablesAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "status",
    )


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ("service_name",)


@admin.register(Employees)
class EmployeesAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name")
