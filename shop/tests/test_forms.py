"""
Tests pour les formulaires
"""
from django.test import TestCase
from decimal import Decimal

from shop.forms import (
    CustomUserCreationForm, ProductForm, CheckoutForm,
    UserPreferencesForm, AdminUserEditForm
)
from shop.models import User, Category, Product, Order


class CustomUserCreationFormTest(TestCase):
    """Tests pour le formulaire d'inscription"""
    
    def setUp(self):
        self.category = Category.objects.create(name='Test')
    
    def test_valid_form(self):
        """Test d'un formulaire valide"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'role': 'customer'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_password_mismatch(self):
        """Test avec mots de passe différents"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'differentpass123',
            'role': 'customer'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_duplicate_username(self):
        """Test avec username déjà utilisé"""
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
        form_data = {
            'username': 'existinguser',
            'email': 'new@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'role': 'customer'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_form_save(self):
        """Test de sauvegarde du formulaire"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'role': 'vendor'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.role, 'vendor')
        self.assertTrue(user.check_password('complexpass123'))


class ProductFormTest(TestCase):
    """Tests pour le formulaire de produit"""
    
    def setUp(self):
        self.vendor = User.objects.create_user(
            username='vendor',
            email='vendor@example.com',
            password='testpass123',
            role='vendor'
        )
        self.category = Category.objects.create(name='Électronique')
    
    def test_valid_form(self):
        """Test d'un formulaire valide"""
        form_data = {
            'name': 'New Product',
            'description': 'Product description',
            'price': '25000.00',
            'category': self.category.id,
            'stock': 10
        }
        form = ProductForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_price(self):
        """Test avec prix invalide"""
        form_data = {
            'name': 'New Product',
            'description': 'Description',
            'price': '-100.00',  # Prix négatif
            'category': self.category.id,
            'stock': 10
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_missing_required_fields(self):
        """Test avec champs requis manquants"""
        form_data = {
            'name': 'New Product',
            # Manque description, price, category
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())


class CheckoutFormTest(TestCase):
    """Tests pour le formulaire de checkout"""
    
    def test_valid_form(self):
        """Test d'un formulaire valide"""
        form_data = {
            'shipping_address': '123 Rue Test, Ville',
            'phone': '0123456789',
            'payment_method': 'orange_money',
            'payment_reference': 'REF123456'
        }
        form = CheckoutForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_missing_required_fields(self):
        """Test avec champs requis manquants"""
        form_data = {
            'payment_method': 'orange_money',
            # Manque shipping_address et phone
        }
        form = CheckoutForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_invalid_payment_method(self):
        """Test avec méthode de paiement invalide"""
        form_data = {
            'shipping_address': '123 Rue Test',
            'phone': '0123456789',
            'payment_method': 'invalid_method'
        }
        form = CheckoutForm(data=form_data)
        # Le formulaire Django rejette les valeurs qui ne sont pas dans les choix
        # C'est le comportement attendu - le formulaire devrait être invalide
        self.assertFalse(form.is_valid())
        self.assertIn('payment_method', form.errors)


class UserPreferencesFormTest(TestCase):
    """Tests pour le formulaire de préférences utilisateur"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_valid_form(self):
        """Test d'un formulaire valide"""
        form_data = {
            'username': 'testuser',
            'email': 'updated@example.com',
            'phone': '0123456789',
            'address': '123 Rue Test'
        }
        form = UserPreferencesForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())
    
    def test_form_save(self):
        """Test de sauvegarde du formulaire"""
        form_data = {
            'username': 'testuser',
            'email': 'newemail@example.com',
            'phone': '0987654321',
            'address': 'New Address'
        }
        form = UserPreferencesForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())
        form.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'newemail@example.com')
        self.assertEqual(self.user.phone, '0987654321')


class AdminUserEditFormTest(TestCase):
    """Tests pour le formulaire d'édition admin"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='customer'
        )
    
    def test_valid_form(self):
        """Test d'un formulaire valide"""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'role': 'vendor',
            'is_verified': True,
            'phone': '0123456789',
            'address': 'Test Address'
        }
        form = AdminUserEditForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())
    
    def test_form_save_role_change(self):
        """Test de changement de rôle"""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'role': 'vendor',
            'is_verified': True,
            'phone': '',
            'address': ''
        }
        form = AdminUserEditForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())
        form.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'vendor')
        self.assertTrue(self.user.is_verified)

