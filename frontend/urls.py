from django.urls import path
from .views import *

urlpatterns = [
    path("", home_view, name="home"),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("records/", records_view, name="records"),
    path("records/create/", create_record_view),
    path("records/edit/<int:pk>/", edit_record_view),
    path("records/delete/<int:pk>/", delete_record_view),
   path("logout/", logout_view, name="logout"),
]