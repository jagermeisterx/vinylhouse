from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order


@login_required
def order_list(request):
    orders = Order.objects.filter(usuario=request.user)
    return render(request, "orders/order_list.html", {"orders": orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, usuario=request.user)
    return render(request, "orders/order_detail.html", {"order": order})


@login_required
def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk, usuario=request.user)
    return render(request, "orders/order_success.html", {"order": order})
