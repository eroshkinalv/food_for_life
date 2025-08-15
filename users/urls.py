from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from users.apps import UsersConfig
from users.views import (
    BlockUserView,
    ConfirmEmailView,
    RegisterView,
    UserDetailView,
    UserListView,
    UserCreateView,
    UserUpdateView,
    email_verification,
    PasswordTemplateView,
)

app_name = UsersConfig.name

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="restaurant:home"), name="logout"),
    path(
        "confirm-email/<str:user_email>/",
        ConfirmEmailView.as_view(),
        name="confirm_email",
    ),
    path("user_list/", UserListView.as_view(), name="user_list"),
    path("user_block/<int:user_id>", BlockUserView.as_view(), name="user_block"),
    path("profile/<int:pk>", UserDetailView.as_view(), name="user_profile"),
    path("create_user/", UserCreateView.as_view(), name="users_create"),
    path("list_users/", UserListView.as_view(), name="users_list"),
    path("update_user/<int:pk>/update/", UserUpdateView.as_view(), name="users_update"),
    path("detail_user/<int:pk>/detail/", UserDetailView.as_view(), name="user_profile"),
    path("email_confirm/<str:token>/", email_verification, name="email_confirm"),
    path("change_password/", PasswordTemplateView.as_view(), name="change_password"),
]
