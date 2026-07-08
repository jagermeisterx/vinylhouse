from django.conf import settings
from catalog.models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        cleaned = False
        for item in self.cart.values():
            if "producto" in item or "subtotal" in item:
                item.pop("producto", None)
                item.pop("subtotal", None)
                cleaned = True
        if cleaned:
            self.session.modified = True

    def add(self, producto, cantidad=1):
        producto_id = str(producto.id)
        if producto_id not in self.cart:
            self.cart[producto_id] = {
                "cantidad": 0,
                "precio": str(producto.precio),
            }
        self.cart[producto_id]["cantidad"] += cantidad
        self.save()

    def remove(self, producto):
        producto_id = str(producto.id)
        if producto_id in self.cart:
            del self.cart[producto_id]
            self.save()

    def update(self, producto, cantidad):
        producto_id = str(producto.id)
        if producto_id in self.cart:
            self.cart[producto_id]["cantidad"] = cantidad
            self.save()

    def get_total(self):
        return sum(
            float(item["precio"]) * item["cantidad"]
            for item in self.cart.values()
        )

    def __iter__(self):
        producto_ids = self.cart.keys()
        productos = Product.objects.filter(id__in=producto_ids)
        for producto in productos:
            item = self.cart[str(producto.id)]
            yield {
                "producto": producto,
                "precio": item["precio"],
                "cantidad": item["cantidad"],
                "subtotal": float(item["precio"]) * item["cantidad"],
            }

    def __len__(self):
        return sum(item["cantidad"] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def save(self):
        self.session.modified = True
