from django.urls import path
from . import views

urlpatterns = [
    path("", views.cart_detail, name="cart_detail"),
    path("agregar/<int:producto_id>/", views.cart_add, name="cart_add"),
    path("actualizar/<int:producto_id>/", views.cart_update, name="cart_update"),
    path("quitar/<int:producto_id>/", views.cart_remove, name="cart_remove"),
    path("confirmar/", views.cart_confirm, name="cart_confirm"),
]
