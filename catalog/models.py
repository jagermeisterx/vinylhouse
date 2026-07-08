from django.db import models

class Genre(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Product(models.Model):
    titulo = models.CharField(max_length=150)
    artista = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    genero = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to="productos/", blank=True)
    anio_lanzamiento = models.PositiveIntegerField(null=True, blank=True)
    discogs_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    sello = models.CharField(max_length=200, blank=True)
    formato = models.CharField(max_length=100, blank=True)
    tracklist = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        return f"{self.artista} - {self.titulo}"
