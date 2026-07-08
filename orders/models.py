from django.db import models
from django.contrib.auth.models import User
from catalog.models import Product


class Order(models.Model):
    ESTADOS = [
        ("CONFIRMADA", "Confirmada"),
        ("CANCELADA", "Cancelada"),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="CONFIRMADA")

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"Orden #{self.id} - {self.usuario.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Product, on_delete=models.CASCADE)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.titulo} en Orden #{self.order.id}"
