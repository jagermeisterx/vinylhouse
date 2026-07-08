from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, Genre
from .forms import ProductForm
from .decorators import staff_required


def catalog_list(request):
    genero_id = request.GET.get("genero")
    productos = Product.objects.filter(activo=True)
    if genero_id:
        productos = productos.filter(genero_id=genero_id)
    generos = Genre.objects.all()
    return render(request, "catalog/catalog_list.html", {
        "productos": productos,
        "generos": generos,
        "genero_seleccionado": int(genero_id) if genero_id else None,
    })


def catalog_detail(request, pk):
    producto = get_object_or_404(Product, pk=pk, activo=True)
    return render(request, "catalog/catalog_detail.html", {"producto": producto})


@login_required
@staff_required
def admin_product_list(request):
    productos = Product.objects.all()
    return render(request, "catalog/admin_product_list.html", {"productos": productos})


@login_required
@staff_required
def admin_product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto creado correctamente.")
            return redirect("admin_product_list")
    else:
        form = ProductForm()
    return render(request, "catalog/admin_product_form.html", {"form": form, "accion": "Crear"})


@login_required
@staff_required
def admin_product_edit(request, pk):
    producto = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado correctamente.")
            return redirect("admin_product_list")
    else:
        form = ProductForm(instance=producto)
    return render(request, "catalog/admin_product_form.html", {"form": form, "accion": "Editar"})


@login_required
@staff_required
def admin_product_delete(request, pk):
    producto = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        producto.activo = False
        producto.save()
        messages.success(request, f"Producto '{producto.titulo}' desactivado correctamente.")
        return redirect("admin_product_list")
    return render(request, "catalog/admin_product_confirm_delete.html", {"producto": producto})
