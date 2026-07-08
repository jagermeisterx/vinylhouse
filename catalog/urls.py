from django.urls import path
from . import views

urlpatterns = [
    path("", views.catalog_list, name="catalog_list"),
    path("catalogo/<int:pk>/", views.catalog_detail, name="catalog_detail"),
    path("admin-productos/", views.admin_product_list, name="admin_product_list"),
    path("admin-productos/crear/", views.admin_product_create, name="admin_product_create"),
    path("admin-productos/<int:pk>/editar/", views.admin_product_edit, name="admin_product_edit"),
    path("admin-productos/<int:pk>/eliminar/", views.admin_product_delete, name="admin_product_delete"),
    path("discogs/buscar/", views.discogs_search, name="discogs_search"),
    path("discogs/importar/<int:discogs_id>/", views.discogs_import, name="discogs_import"),
]
