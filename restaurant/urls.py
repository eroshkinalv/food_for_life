from django.urls import path
from restaurant.apps import RestaurantConfig
from restaurant.views import (
    ContactsView,
    AboutRestaurantView,
    ReservationView,
    ConfirmReservationView,
    CancelReservationView,
    ReservationUpdateView,
    ReservationListView,
    ReservationDetailView,
    ReservationDeleteView,
    UpdateReservationStatusView,
    ContactsCreateView,
    HomePageListView,
    ChangesView,
    RestaurantUpdateView,
    RestaurantCreateView,
    ServicesUpdateView,
    ServicesCreateView,
    TablesCreateView,
    TablesUpdateView,
    EmployeesCreateView,
    EmployeesUpdateView,
    MenuUpdateView,
    MenuCreateView,
    ServicesListView,
    ServicesDeleteView,
    ServicesDetailView,
    TablesListView,
    TablesDetailView,
    TablesDeleteView,
    EmployeesListView,
    EmployeesDetailView,
    EmployeesDeleteView,
    MenuListView,
    MenuDetailView,
    MenuDeleteView,
)

app_name = RestaurantConfig.name


class HomePageUpdateView:
    pass


urlpatterns = [
    path("", HomePageListView.as_view(), name="home"),
    path("restaurant/create/", RestaurantCreateView.as_view(), name="restaurant_create"),
    path("restaurant/<int:pk>/update/", RestaurantUpdateView.as_view(), name="restaurant_update"),
    path("service/create/", ServicesCreateView.as_view(), name="service_create"),
    path("service/list/", ServicesListView.as_view(), name="service_list"),
    path("service/<int:pk>/update/", ServicesUpdateView.as_view(), name="service_update"),
    path("service/<int:pk>/detail/", ServicesDetailView.as_view(), name="service_detail"),
    path("service/<int:pk>/delete/", ServicesDeleteView.as_view(), name="service_delete"),
    path("tables/create/", TablesCreateView.as_view(), name="tables_create"),
    path("tables/list/", TablesListView.as_view(), name="tables_list"),
    path("tables/<int:pk>/update/", TablesUpdateView.as_view(), name="tables_update"),
    path("tables/<int:pk>/detail/", TablesDetailView.as_view(), name="tables_detail"),
    path("tables/<int:pk>/delete/", TablesDeleteView.as_view(), name="tables_delete"),
    path("employees/create/", EmployeesCreateView.as_view(), name="employees_create"),
    path("employees/list/", EmployeesListView.as_view(), name="employees_list"),
    path("employees/<int:pk>/update/", EmployeesUpdateView.as_view(), name="employees_update"),
    path("employees/<int:pk>/detail/", EmployeesDetailView.as_view(), name="employees_detail"),
    path("employees/<int:pk>/delete/", EmployeesDeleteView.as_view(), name="employees_delete"),
    path("menu/create/", MenuCreateView.as_view(), name="menu_create"),
    path("menu/list/", MenuListView.as_view(), name="menu_list"),
    path("menu/<int:pk>/update/", MenuUpdateView.as_view(), name="menu_update"),
    path("menu/<int:pk>/detail/", MenuDetailView.as_view(), name="menu_detail"),
    path("menu/<int:pk>/update/", MenuDeleteView.as_view(), name="menu_delete"),
    path("changes/", ChangesView.as_view(), name="changes"),
    path("reservation/", ReservationView.as_view(), name="reservation"),
    path("contacts/", ContactsView.as_view(), name="contacts"),
    path("contacts/create/", ContactsCreateView.as_view(), name="contacts_create"),
    path("about_restaurant/", AboutRestaurantView.as_view(), name="about_restaurant"),
    path("confirm_reservation/<int:reservation_id>/", ConfirmReservationView.as_view(), name="confirm_reservation"),
    path("cancel_reservation/<int:pk>/", CancelReservationView.as_view(), name="cancel_reservation"),
    path("reservation/<int:pk>/update/", ReservationUpdateView.as_view(), name="reservation_update"),
    path("list/", ReservationListView.as_view(), name="reservation_list"),
    path("detail/<int:id>", ReservationDetailView.as_view(), name="reservation_detail"),
    path("delete/<int:pk>/", ReservationDeleteView.as_view(), name="reservation_delete"),
    path("update_status/<int:reservation_id>/", UpdateReservationStatusView.as_view(), name="update_status"),
]
