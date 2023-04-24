from delivery import views
from django.urls import path, re_path

urlpatterns = [
    re_path("signup/", views.signup, name = "signup"),
    re_path("login/", views.login, name = "login"),
    re_path("logout/", views.logout, name = "logout"),
    re_path("reset/", views.reset_password, name = "reset_password"),
    re_path("get_deliveries/", views.get_deliveries, name = "get_deliveries"),
    re_path("get_location/", views.get_location, name = "get_location"),
    re_path("get_orders/", views.get_orders, name = "get_orders"),
    re_path("get_customers/", views.get_customers, name = "get_customers"),
    re_path("add_service/", views.add_service, name = "add_service"),
    re_path("place_order/", views.place_order, name = "place_order")
]
