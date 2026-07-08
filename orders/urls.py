from django.urls import path
from . import views

urlpatterns = [
    path("mis-ordenes/", views.order_list, name="order_list"),
    path("mis-ordenes/<int:pk>/", views.order_detail, name="order_detail"),
    path("ordenes/<int:pk>/exito/", views.order_success, name="order_success"),
]
