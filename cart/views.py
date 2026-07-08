from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from catalog.models import Product
from .cart import Cart


@login_required
def cart_detail(request):
    cart = Cart(request)
    return render(request, "cart/cart_detail.html", {"cart": cart})


@login_required
def cart_add(request, producto_id):
    producto = get_object_or_404(Product, pk=producto_id, activo=True)
    cart = Cart(request)
    cantidad = int(request.POST.get("cantidad", 1))
    if cantidad < 1:
        messages.error(request, "La cantidad mínima es 1.")
        return redirect("catalog_detail", pk=producto_id)
    if cantidad > producto.stock:
        messages.error(request, f"No hay suficiente stock. Stock disponible: {producto.stock}")
        return redirect("catalog_detail", pk=producto_id)
    cart.add(producto, cantidad)
    messages.success(request, f"{producto.titulo} agregado al carrito.")
    return redirect("cart_detail")


@login_required
def cart_update(request, producto_id):
    producto = get_object_or_404(Product, pk=producto_id)
    cart = Cart(request)
    cantidad = int(request.POST.get("cantidad", 1))
    if cantidad < 1:
        messages.error(request, "La cantidad mínima es 1.")
        return redirect("cart_detail")
    if cantidad > producto.stock:
        messages.error(request, f"No hay suficiente stock. Stock disponible: {producto.stock}")
        return redirect("cart_detail")
    cart.update(producto, cantidad)
    messages.success(request, "Cantidad actualizada.")
    return redirect("cart_detail")


@login_required
def cart_remove(request, producto_id):
    producto = get_object_or_404(Product, pk=producto_id)
    cart = Cart(request)
    cart.remove(producto)
    messages.success(request, f"{producto.titulo} quitado del carrito.")
    return redirect("cart_detail")


@login_required
def cart_confirm(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, "El carrito está vacío.")
        return redirect("cart_detail")

    for item in cart:
        producto = item["producto"]
        if not producto.activo:
            messages.error(request, f"'{producto.titulo}' ya no está disponible. Se ha quitado del carrito.")
            cart.remove(producto)
            return redirect("cart_detail")
        if item["cantidad"] > producto.stock:
            messages.error(
                request,
                f"Stock insuficiente para '{producto.titulo}'. Disponible: {producto.stock}",
            )
            return redirect("cart_detail")

    from django.db import transaction
    from orders.models import Order, OrderItem

    with transaction.atomic():
        order = Order.objects.create(
            usuario=request.user,
            total=cart.get_total(),
        )
        for item in cart:
            producto = item["producto"]
            OrderItem.objects.create(
                order=order,
                producto=producto,
                precio_unitario=item["precio"],
                cantidad=item["cantidad"],
                subtotal=float(item["precio"]) * item["cantidad"],
            )
            producto.stock -= item["cantidad"]
            producto.save()
        cart.clear()

    messages.success(request, f"¡Compra exitosa! Tu orden #{order.id} ha sido registrada.")
    return redirect("order_success", pk=order.id)
