from django.contrib import admin
from .models import Genre, Product


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "titulo",
        "artista",
        "genero",
        "precio",
        "stock",
        "activo",
        "discogs_id",
    )
    list_filter = ("activo", "genero")
    list_editable = ("precio", "stock", "activo")
    search_fields = ("titulo", "artista", "discogs_id", "sello")
    readonly_fields = ("discogs_id", "creado_en", "actualizado_en")
    fieldsets = (
        ("General", {
            "fields": ("titulo", "artista", "descripcion", "genero", "imagen"),
        }),
        ("Comercial", {
            "fields": ("precio", "stock", "activo"),
        }),
        ("Datos técnicos", {
            "fields": (
                "anio_lanzamiento", "sello", "formato", "tracklist", "discogs_id",
            ),
            "classes": ("collapse",),
        }),
        ("Auditoría", {
            "fields": ("creado_en", "actualizado_en"),
            "classes": ("collapse",),
        }),
    )
