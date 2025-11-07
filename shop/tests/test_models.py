"""
Tests pour les modèles
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

from shop.models import (
    User, Category, Product, Cart, Order, OrderItem,
    PasswordResetToken, Notification, Tag
)


class UserModelTest(TestCase):
    """Tests pour le modèle User"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='customer'
        )
    
    def test_user_creation(self):
        """Test de création d'un utilisateur"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.role, 'customer')
        self.assertFalse(self.user.is_verified)
    
    def test_user_str(self):
        """Test de la méthode __str__"""
        self.assertEqual(str(self.user), 'testuser')
    
    def test_vendor_user(self):
        """Test de création d'un vendeur"""
        vendor = User.objects.create_user(
            username='vendor',
            email='vendor@example.com',
            password='testpass123',
            role='vendor'
        )
        self.assertEqual(vendor.role, 'vendor')


class CategoryModelTest(TestCase):
    """Tests pour le modèle Category"""
    
    def test_category_creation(self):
        """Test de création d'une catégorie"""
        category = Category.objects.create(name='Électronique')
        self.assertEqual(category.name, 'Électronique')
        self.assertIsNotNone(category.slug)
        self.assertEqual(category.slug, 'electronique')
    
    def test_category_auto_slug(self):
        """Test de génération automatique du slug"""
        category = Category.objects.create(name='Vêtements & Mode')
        self.assertEqual(category.slug, 'vetements-mode')
    
    def test_category_str(self):
        """Test de la méthode __str__"""
        category = Category.objects.create(name='Test')
        self.assertEqual(str(category), 'Test')


class ProductModelTest(TestCase):
    """Tests pour le modèle Product"""
    
    def setUp(self):
        self.vendor = User.objects.create_user(
            username='vendor',
            email='vendor@example.com',
            password='testpass123',
            role='vendor'
        )
        self.category = Category.objects.create(name='Électronique')
    
    def test_product_creation(self):
        """Test de création d'un produit"""
        product = Product.objects.create(
            vendor=self.vendor,
            name='Smartphone',
            description='Un super smartphone',
            price=Decimal('50000.00'),
            category=self.category,
            stock=10
        )
        self.assertEqual(product.name, 'Smartphone')
        self.assertEqual(product.price, Decimal('50000.00'))
        self.assertEqual(product.stock, 10)
        self.assertTrue(product.is_active)
    
    def test_product_formatted_price(self):
        """Test du formatage du prix"""
        product = Product.objects.create(
            vendor=self.vendor,
            name='Test',
            description='Test',
            price=Decimal('50000.00'),
            category=self.category
        )
        self.assertEqual(product.formatted_price(), '50000 FCFA')
    
    def test_product_str(self):
        """Test de la méthode __str__"""
        product = Product.objects.create(
            vendor=self.vendor,
            name='Test Product',
            description='Test',
            price=Decimal('10000.00'),
            category=self.category
        )
        self.assertEqual(str(product), 'Test Product')


class CartModelTest(TestCase):
    """Tests pour le modèle Cart"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='testpass123',
            role='customer'
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
            name='Product',
            description='Test',
            price=Decimal('10000.00'),
            category=self.category,
            stock=5
        )
    
    def test_cart_creation(self):
        """Test de création d'un panier"""
        cart = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=2
        )
        self.assertEqual(cart.user, self.user)
        self.assertEqual(cart.product, self.product)
        self.assertEqual(cart.quantity, 2)
    
    def test_cart_total_price(self):
        """Test du calcul du prix total"""
        cart = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=3
        )
        expected_total = Decimal('10000.00') * 3
        self.assertEqual(cart.total_price(), expected_total)
    
    def test_cart_formatted_total(self):
        """Test du formatage du total"""
        cart = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=2
        )
        self.assertEqual(cart.formatted_total(), '20000 FCFA')
    
    def test_cart_unique_together(self):
        """Test de l'unicité user-product"""
        Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=1
        )
        # Essayer de créer un doublon devrait créer une erreur IntegrityError
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Cart.objects.create(
                user=self.user,
                product=self.product,
                quantity=2
            )


class OrderModelTest(TestCase):
    """Tests pour le modèle Order"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='testpass123',
            role='customer'
        )
    
    def test_order_creation(self):
        """Test de création d'une commande"""
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('50000.00'),
            status='pending',
            payment_method='orange_money',
            shipping_address='123 Rue Test',
            phone='0123456789'
        )
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.total_price, Decimal('50000.00'))
        self.assertFalse(order.receipt_sent)
    
    def test_order_formatted_total(self):
        """Test du formatage du total"""
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('50000.00'),
            shipping_address='Test',
            phone='0123456789'
        )
        self.assertEqual(order.formatted_total(), '50000 FCFA')
    
    def test_order_str(self):
        """Test de la méthode __str__"""
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('10000.00'),
            shipping_address='Test',
            phone='0123456789'
        )
        self.assertIn('Commande #', str(order))
        self.assertIn('customer', str(order))


class OrderItemModelTest(TestCase):
    """Tests pour le modèle OrderItem"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='testpass123',
            role='customer'
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
            name='Product',
            description='Test',
            price=Decimal('10000.00'),
            category=self.category
        )
        self.order = Order.objects.create(
            user=self.user,
            total_price=Decimal('30000.00'),
            shipping_address='Test',
            phone='0123456789'
        )
    
    def test_order_item_creation(self):
        """Test de création d'un article de commande"""
        order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=3,
            price=Decimal('10000.00')
        )
        self.assertEqual(order_item.order, self.order)
        self.assertEqual(order_item.product, self.product)
        self.assertEqual(order_item.quantity, 3)
    
    def test_order_item_total(self):
        """Test du calcul du total"""
        order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=Decimal('10000.00')
        )
        expected_total = Decimal('10000.00') * 2
        self.assertEqual(order_item.total(), expected_total)


class PasswordResetTokenModelTest(TestCase):
    """Tests pour le modèle PasswordResetToken"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_token_creation(self):
        """Test de création d'un token"""
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='test-token-123',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        self.assertEqual(token.user, self.user)
        self.assertFalse(token.is_used)
    
    def test_token_expired(self):
        """Test de vérification d'expiration"""
        expired_token = PasswordResetToken.objects.create(
            user=self.user,
            token='expired-token',
            expires_at=timezone.now() - timedelta(hours=1)
        )
        self.assertTrue(expired_token.is_expired())
    
    def test_token_not_expired(self):
        """Test de vérification de non-expiration"""
        valid_token = PasswordResetToken.objects.create(
            user=self.user,
            token='valid-token',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        self.assertFalse(valid_token.is_expired())


class NotificationModelTest(TestCase):
    """Tests pour le modèle Notification"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.order = Order.objects.create(
            user=self.user,
            total_price=Decimal('10000.00'),
            shipping_address='Test',
            phone='0123456789'
        )
    
    def test_notification_creation(self):
        """Test de création d'une notification"""
        notification = Notification.objects.create(
            user=self.user,
            type='order_status',
            message='Votre commande a été livrée',
            related_order=self.order
        )
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.type, 'order_status')
        self.assertFalse(notification.is_read)
    
    def test_notification_str(self):
        """Test de la méthode __str__"""
        notification = Notification.objects.create(
            user=self.user,
            type='new_order',
            message='Nouvelle commande'
        )
        self.assertIn('testuser', str(notification))
        self.assertIn('Nouvelle commande', str(notification))


class TagModelTest(TestCase):
    """Tests pour le modèle Tag"""
    
    def test_tag_creation(self):
        """Test de création d'un tag"""
        tag = Tag.objects.create(name='Nouveau')
        self.assertEqual(tag.name, 'Nouveau')
    
    def test_tag_str(self):
        """Test de la méthode __str__"""
        tag = Tag.objects.create(name='Promo')
        self.assertEqual(str(tag), 'Promo')

