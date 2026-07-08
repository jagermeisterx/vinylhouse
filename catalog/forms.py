from django import forms
from .models import Product, Genre


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["titulo", "artista", "descripcion", "genero", "precio", "stock", "imagen", "anio_lanzamiento"]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_precio(self):
        precio = self.cleaned_data["precio"]
        if precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor a 0.")
        return precio

    def clean_stock(self):
        stock = self.cleaned_data["stock"]
        if stock < 0:
            raise forms.ValidationError("El stock no puede ser negativo.")
        return stock
