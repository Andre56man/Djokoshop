"""
Tests pour les context processors
"""
from django.test import TestCase, RequestFactory
from decimal import Decimal

from shop.models import User, Category, Product, Cart, Notification
from shop.context_processors import cart


class CartContextProcessorTest(TestCase):
    """Tests pour le context processor du panier"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.vendor = User.objects.create_user(
            username='vendor',
            email='vendor@example.com',
            password='testpass123',
            role='vendor'
        )
        self.category = Category.objects.create(name='Test')
        self.product = Product.objects.create(
            vendor=self.vendor,
            name='Test Product',
            description='Test',
            price=Decimal('10000.00'),
            category=self.category
        )
    
    def test_cart_context_anonymous_user(self):
        """Test du context processor pour un utilisateur anonyme"""
        from django.contrib.auth.models import AnonymousUser
        request = self.factory.get('/')
        request.user = AnonymousUser()
        
        context = cart(request)
        self.assertEqual(context['cart_count'], 0)
        self.assertEqual(context['notifications_count'], 0)
    
    def test_cart_context_authenticated_user_empty_cart(self):
        """Test du context processor pour un utilisateur avec panier vide"""
        request = self.factory.get('/')
        request.user = self.user
        
        context = cart(request)
        self.assertEqual(context['cart_count'], 0)
        self.assertEqual(context['notifications_count'], 0)
    
    def test_cart_context_with_items(self):
        """Test du context processor avec des articles dans le panier"""
        # Créons des produits différents car unique_together empêche d'avoir le même produit deux fois
        product2 = Product.objects.create(
            vendor=self.vendor,
            name='Product 2',
            description='Test',
            price=Decimal('20000.00'),
            category=self.category
        )
        
        Cart.objects.create(user=self.user, product=self.product, quantity=1)
        Cart.objects.create(user=self.user, product=product2, quantity=2)
        
        request = self.factory.get('/')
        request.user = self.user
        
        context = cart(request)
        self.assertEqual(context['cart_count'], 2)
    
    def test_cart_context_with_notifications(self):
        """Test du context processor avec des notifications"""
        Notification.objects.create(
            user=self.user,
            type='order_status',
            message='Test notification 1',
            is_read=False
        )
        Notification.objects.create(
            user=self.user,
            type='new_order',
            message='Test notification 2',
            is_read=False
        )
        Notification.objects.create(
            user=self.user,
            type='order_status',
            message='Test notification 3',
            is_read=True
        )
        
        request = self.factory.get('/')
        request.user = self.user
        
        context = cart(request)
        self.assertEqual(context['notifications_count'], 2)  # Seulement les non lues
    
    def test_cart_context_multiple_users(self):
        """Test que le context processor retourne les bonnes données pour chaque utilisateur"""
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        
        # Articles pour user1
        Cart.objects.create(user=self.user, product=self.product, quantity=1)
        
        # Articles pour user2
        product2 = Product.objects.create(
            vendor=self.vendor,
            name='Product 2',
            description='Test',
            price=Decimal('20000.00'),
            category=self.category
        )
        Cart.objects.create(user=user2, product=product2, quantity=3)
        
        # Vérifier pour user1
        request1 = self.factory.get('/')
        request1.user = self.user
        context1 = cart(request1)
        self.assertEqual(context1['cart_count'], 1)
        
        # Vérifier pour user2
        request2 = self.factory.get('/')
        request2.user = user2
        context2 = cart(request2)
        self.assertEqual(context2['cart_count'], 1)  # 1 article unique

