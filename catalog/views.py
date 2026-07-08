from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from .models import Product, Genre
from .forms import ProductForm
from .decorators import staff_required
from . import discogs_service


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


@login_required
@staff_required
def discogs_search(request):
    query = request.GET.get("q", "").strip()
    search_result = None
    if query:
        try:
            search_result = discogs_service.search_releases(query)
        except Exception as e:
            messages.error(request, f"Error al buscar en Discogs: {e}")
            search_result = {"results": [], "count": 0, "pages": 0, "page": 0}
    return render(request, "catalog/discogs_search.html", {
        "query": query,
        "search_result": search_result,
    })


@login_required
@staff_required
def discogs_import(request, discogs_id):
    if request.method != "POST":
        return redirect("discogs_search")
    if Product.objects.filter(discogs_id=str(discogs_id)).exists():
        existing = Product.objects.get(discogs_id=str(discogs_id))
        messages.error(
            request,
            f"Este release ya fue importado como producto #{existing.id} '{existing.titulo}'. "
            f"<a href='/admin-productos/{existing.id}/editar/'>Editar el existente</a>.",
        )
        return redirect("discogs_search")
    try:
        rel = discogs_service.get_release(discogs_id)
    except Exception as e:
        messages.error(request, f"No se pudo obtener el release de Discogs: {e}")
        return redirect("discogs_search")
    genero_obj, _ = Genre.objects.get_or_create(
        nombre=rel["genero"],
    )
    producto = Product(
        titulo=rel["titulo"][:150],
        artista=rel["artista"][:150],
        descripcion=rel["descripcion"],
        genero=genero_obj,
        precio=0,
        stock=0,
        anio_lanzamiento=rel["anio_lanzamiento"],
        discogs_id=str(rel["discogs_id"]),
        sello=rel["sello"][:200],
        formato=rel["formato"][:100],
        tracklist=rel["tracklist"],
    )
    if rel["imagen_url"]:
        try:
            placeholder, ext, data = discogs_service.download_image(rel["imagen_url"])
            img_name = f"discogs_{rel['discogs_id']}.{ext}"
            producto.imagen.save(img_name, ContentFile(data), save=False)
        except Exception as e:
            messages.warning(request, f"No se pudo descargar la imagen: {e}")
    producto.save()
    messages.success(
        request,
        f"Producto '{producto.titulo}' importado. Revisa precio y stock.",
    )
    return redirect("admin_product_edit", pk=producto.id)
