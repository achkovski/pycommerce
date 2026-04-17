from .cart import Cart


def cart(request):
    return {'cart_item_count': len(Cart(request))}
