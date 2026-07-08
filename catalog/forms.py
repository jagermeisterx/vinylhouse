from django import forms
from .models import Product, Genre


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "titulo", "artista", "descripcion", "genero", "precio", "stock",
            "imagen", "anio_lanzamiento", "sello", "formato", "tracklist",
        ]
        labels = {
            "titulo": "Título",
            "artista": "Artista",
            "descripcion": "Descripción",
            "genero": "Género",
            "precio": "Precio",
            "stock": "Stock",
            "imagen": "Imagen de portada",
            "anio_lanzamiento": "Año de lanzamiento",
            "sello": "Sello discográfico",
            "formato": "Formato",
            "tracklist": "Lista de pistas",
        }
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "artista": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "genero": forms.Select(attrs={"class": "form-select"}),
            "precio": forms.NumberInput(attrs={"class": "form-control"}),
            "stock": forms.NumberInput(attrs={"class": "form-control"}),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "anio_lanzamiento": forms.NumberInput(attrs={"class": "form-control"}),
            "sello": forms.TextInput(attrs={"class": "form-control"}),
            "formato": forms.TextInput(attrs={"class": "form-control"}),
            "tracklist": forms.Textarea(attrs={"class": "form-control", "rows": 6}),
        }

    def clean_precio(self):
        precio = self.cleaned_data["precio"]
        if precio < 0:
            raise forms.ValidationError("El precio no puede ser negativo.")
        return precio

    def clean_stock(self):
        stock = self.cleaned_data["stock"]
        if stock < 0:
            raise forms.ValidationError("El stock no puede ser negativo.")
        return stock
