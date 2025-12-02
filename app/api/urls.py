from django.urls import path
from . import views

urlpatterns = [
    path("users", views.get_users, name="get_users"),
    path("users/add", views.add_user, name="add_user"),
    path("users/update", views.update_user, name="update_user"),
    path("users/delete", views.delete_user, name="delete_user"),
    path("orders", views.get_orders, name="get_orders"),
    path("orders/add", views.add_order, name="add_order"),
    path("orders/update", views.update_order, name="update_order"),
    path("orders/delete", views.delete_order, name="delete_order"),
]
