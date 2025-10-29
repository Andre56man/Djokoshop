from .models import Cart, Notification

def cart(request):
    """Add cart count and notifications to context"""
    cart_count = 0
    notifications_count = 0
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()
        notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return {
        'cart_count': cart_count,
        'notifications_count': notifications_count
    }

