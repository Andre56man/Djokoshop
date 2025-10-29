from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.core.mail import send_mail
from django.utils import timezone
from django.template.loader import render_to_string
from decimal import Decimal
import random
import secrets
from datetime import timedelta

from .models import (User, Category, Product, Cart, Order, OrderItem,
                    PasswordResetToken, Notification)
from .forms import (
    CustomUserCreationForm, ProductForm, CheckoutForm, 
    UserPreferencesForm, AdminUserEditForm
)


def is_vendor(user):
    return user.role == 'vendor'


def is_admin(user):
    return user.role == 'admin' or user.is_superuser


def home(request):
    """Page d'accueil avec produits"""
    products = Product.objects.filter(is_active=True)[:12]
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'shop/home.html', context)


def product_list(request):
    category_id = request.GET.get('category')
    search_query = request.GET.get('search', '')

    products = Product.objects.all()
    selected_category = None  # ✅ variable pour le nom de la catégorie sélectionnée

    if category_id:
        selected_category = get_object_or_404(Category, id=category_id)
        products = products.filter(category=selected_category)

    if search_query:
        products = products.filter(name__icontains=search_query)

    paginator = Paginator(products, 6)  # ✅ limite à 6 produits par page
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    categories = Category.objects.all()

    return render(request, 'shop/product_list.html', {
        'products': products_page,
        'categories': categories,
        'selected_category': selected_category,  # ✅ on passe la catégorie sélectionnée au template
    })



def product_detail(request, pk):
    """Détails d'un produit"""
    product = get_object_or_404(Product, pk=pk, is_active=True)
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(pk=pk)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'shop/product_detail.html', context)


def send_verification_email(user):
    """Envoyer un email de vérification"""
    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    user.verification_code = code
    user.verification_code_sent_at = timezone.now()
    user.save()
    
    subject = 'Confirmez votre compte - Ma Boutique'
    message = f"""Bonjour {user.username},

Votre code de vérification est: {code}

Entrez ce code sur le site pour confirmer votre compte.

Si vous n'avez pas créé de compte, ignorez cet email.

Cordialement,
L'équipe Ma Boutique"""
    
    from django.conf import settings
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        print(f"Email de vérification envoyé à {user.email} avec le code {code}")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email à {user.email}: {e}")


def register(request):
    """Inscription"""
    if request.method == 'POST':
        print("POST request reçu")
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            print("Formulaire valide")
            user = form.save()
            
            # Envoyer code de vérification
            send_verification_email(user)
            
            login(request, user)
            messages.success(request, f'Inscription réussie! Un code de vérification a été envoyé à {user.email}. Vérifiez votre email.')
            return redirect('verify_email')
        else:
            print(f"Formulaire invalide: {form.errors}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'shop/register.html', {'form': form})


def login_view(request):
    """Connexion"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Connexion réussie!')
            return redirect('home')
        else:
            messages.error(request, 'Identifiants invalides')
    
    return render(request, 'shop/login.html')


@login_required
def cart_view(request):
    """Voir le panier"""
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'shop/cart.html', context)


@login_required
def add_to_cart(request, product_id):
    """Ajouter un produit au panier"""
    product = get_object_or_404(Product, pk=product_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if created:
            # Notification au vendeur pour le nouveau produit dans le panier
            Notification.objects.create(
                user=product.vendor,
                type='new_order',
                message=f"Votre produit '{product.name}' a été ajouté au panier par {request.user.username}",
                related_user=request.user
            )
        else:
            cart_item.quantity += quantity
            cart_item.save()
        
        messages.success(request, f'{product.name} ajouté au panier')
    
    return redirect('cart')


@login_required
def remove_from_cart(request, cart_id):
    """Retirer un produit du panier"""
    cart_item = get_object_or_404(Cart, pk=cart_id, user=request.user)
    cart_item.delete()
    messages.success(request, 'Produit retiré du panier')
    return redirect('cart')


@login_required
def checkout(request):
    """Passer commande"""
    cart_items = Cart.objects.filter(user=request.user)
    
    if not cart_items:
        messages.error(request, 'Votre panier est vide')
        return redirect('cart')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Calculer le total
            total = sum(item.total_price() for item in cart_items)
            
            # Créer la commande
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = total
            order.save()
            
            # Créer les articles de commande
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
            
            # Vider le panier
            cart_items.delete()
            
            # Envoyer le reçu par email
            send_order_receipt(order)
            
            messages.success(request, 'Commande passée avec succès! Un reçu a été envoyé à votre email.')
            return redirect('order_detail', order_id=order.id)
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = CheckoutForm()
    
    total = sum(item.total_price() for item in cart_items)
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'shop/checkout.html', context)


@login_required
def order_detail(request, order_id):
    """Détails d'une commande"""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'shop/order_detail.html', context)


@login_required
def my_orders(request):
    """Mes commandes"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'shop/my_orders.html', context)


@login_required
@user_passes_test(is_vendor)
def vendor_dashboard(request):
    """Tableau de bord vendeur"""
    products = Product.objects.filter(vendor=request.user)
    orders = OrderItem.objects.filter(product__vendor=request.user).order_by('-order__created_at')[:10]
    
    # Statistiques
    total_products = products.count()
    active_products = products.filter(is_active=True).count()
    total_sales = OrderItem.objects.filter(product__vendor=request.user).count()
    
    context = {
        'total_products': total_products,
        'active_products': active_products,
        'total_sales': total_sales,
        'products': products[:10],
        'orders': orders,
    }
    return render(request, 'shop/vendor_dashboard.html', context)


@login_required
@user_passes_test(is_vendor)
def vendor_update_order_status(request, order_id):
    """Permet au vendeur de modifier le statut d'une commande liée à ses produits.

    Autorise uniquement si la commande contient au moins un OrderItem dont le produit appartient au vendeur.
    Le vendeur peut définir le statut sur 'pending' (En attente) ou 'delivered' (Livrée).
    """
    order = get_object_or_404(Order, pk=order_id)

    # Vérifier que l'ordre contient au moins un item du vendeur
    has_item_for_vendor = OrderItem.objects.filter(order=order, product__vendor=request.user).exists()
    if not has_item_for_vendor:
        messages.error(request, "Vous n'êtes pas autorisé à modifier cette commande.")
        return redirect('vendor_dashboard')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        allowed = ['pending', 'delivered','delivering','cancel']
        if new_status not in allowed:
            messages.error(request, 'Statut invalide.')
            return redirect('vendor_dashboard')

        old_status = order.status
        order.status = new_status
        order.save()
        
        # Notification au client du changement de statut
        status_display = dict(Order.STATUS_CHOICES).get(new_status, new_status)
        Notification.objects.create(
            user=order.user,
            type='order_status',
            message=f"Le statut de votre commande #{order.id} est passé à '{status_display}'",
            related_order=order
        )
        
        # Si la commande est livrée, notifier l'admin
        if new_status == 'delivered':
            admins = User.objects.filter(role='admin') | User.objects.filter(is_superuser=True)
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    type='delivered_order',
                    message=f"La commande #{order.id} a été marquée comme livrée",
                    related_order=order
                )
        
        messages.success(request, f"Le statut de la commande #{order.id} a été mis à jour en '{new_status}'.")
    return redirect('vendor_dashboard')


@login_required
@user_passes_test(is_vendor)

@login_required
@user_passes_test(is_vendor)
def vendor_add_product(request):
    """Ajouter un produit"""
    categories = Category.objects.all()
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user
            product.save()
            form.save_m2m()
            messages.success(request, 'Produit ajouté avec succès!')
            return redirect('vendor_dashboard')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'categories': categories,
    }
    return render(request, 'shop/vendor_add_product.html', context)


@login_required
@user_passes_test(is_vendor)
def vendor_edit_product(request, pk):
    """Modifier un produit"""
    product = get_object_or_404(Product, pk=pk, vendor=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produit modifié avec succès!')
            return redirect('vendor_dashboard')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
    }
    return render(request, 'shop/vendor_edit_product.html', context)


@login_required
@user_passes_test(is_vendor)
def vendor_delete_product(request, pk):
    """Supprimer un produit"""
    product = get_object_or_404(Product, pk=pk, vendor=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Produit supprimé!')
    return redirect('vendor_dashboard')


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Tableau de bord admin"""
    total_users = User.objects.count()
    total_vendors = User.objects.filter(role='vendor').count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    
    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    
    context = {
        'total_users': total_users,
        'total_vendors': total_vendors,
        'total_products': total_products,
        'total_orders': total_orders,
        'recent_orders': recent_orders,
    }
    return render(request, 'shop/admin_dashboard.html', context)


def privacy_policy(request):
    return render(request, 'shop/privacy.html')


@login_required
def notifications_list(request):
    """Liste des notifications de l'utilisateur"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, notification_id):
    """Marquer une notification comme lue"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})

@login_required
def mark_all_notifications_read(request):
    """Marquer toutes les notifications comme lues"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})


@login_required
def verify_email(request):
    """Vérifier le code de confirmation email"""
    if request.method == 'POST':
        code = request.POST.get('code')
        
        if code == request.user.verification_code:
            request.user.is_verified = True
            request.user.verification_code = ''
            request.user.save()
            messages.success(request, 'Email vérifié avec succès!')
            return redirect('home')
        else:
            messages.error(request, 'Code invalide')
    
    return render(request, 'shop/verify_email.html')


@login_required
def resend_verification_code(request):
    """Renvoyer le code de vérification"""
    send_verification_email(request.user)
    messages.success(request, 'Code de vérification renvoyé!')
    return redirect('verify_email')


def forgot_password(request):
    """Demande de réinitialisation de mot de passe"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Créer un token de réinitialisation
            token = secrets.token_urlsafe(32)
            expires_at = timezone.now() + timedelta(hours=1)
            
            PasswordResetToken.objects.create(
                user=user,
                token=token,
                expires_at=expires_at
            )
            
            # Envoyer email
            subject = 'Réinitialisation de votre mot de passe'
            reset_url = request.build_absolute_uri(f'/reset-password/{token}/')
            message = f"""
            Bonjour {user.username},
            
            Vous avez demandé la réinitialisation de votre mot de passe.
            
            Cliquez sur ce lien pour réinitialiser votre mot de passe:
            {reset_url}
            
            Ce lien est valable pendant 1 heure.
            
            Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.
            
            Cordialement,
            L'équipe Ma Boutique
            """
            
            from django.conf import settings
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            messages.success(request, f'Un lien de réinitialisation a été envoyé à {email}')
            return redirect('login')
            
        except User.DoesNotExist:
            messages.error(request, "Aucun compte trouvé avec cet email")
    
    return render(request, 'shop/forgot_password.html')


def reset_password(request, token):
    """Réinitialiser le mot de passe"""
    try:
        reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
        
        if reset_token.is_expired():
            messages.error(request, 'Ce lien a expiré')
            reset_token.delete()
            return redirect('forgot_password')
        
        if request.method == 'POST':
            new_password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            if new_password != confirm_password:
                messages.error(request, 'Les mots de passe ne correspondent pas')
            elif len(new_password) < 8:
                messages.error(request, 'Le mot de passe doit contenir au moins 8 caractères')
            else:
                user = reset_token.user
                user.set_password(new_password)
                user.save()
                
                reset_token.is_used = True
                reset_token.save()
                
                messages.success(request, 'Mot de passe modifié avec succès!')
                return redirect('login')
        
        return render(request, 'shop/reset_password.html', {'token': token})
        
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Lien invalide')
        return redirect('forgot_password')


def send_order_receipt(order):
    """Envoyer le reçu de commande par email"""
    try:
        from django.conf import settings
        
        items_text = ""
        locations = []
        
        for item in order.items.all():
            items_text += f"\n{item.product.name} - {item.quantity} x {item.price} FCFA = {int(item.product.price * item.quantity)} FCFA"
            if item.product.location:
                locations.append(f"{item.product.name}: {item.product.location}")
            if item.product.warehouse_address:
                locations.append(f"{item.product.name} (Entrepôt): {item.product.warehouse_address}")
        
        locations_text = "\n".join([f"• {loc}" for loc in locations]) if locations else "Non spécifié"
        
        subject = f'Reçu de commande #{order.id} - DJOKO SHOP'
        message = f"""Bonjour {order.user.username},

Merci pour votre commande sur DJOKO SHOP!

DÉTAILS DE LA COMMANDE:
Commande #{order.id}
Date: {order.created_at.strftime("%d/%m/%Y %H:%M")}

MÉTHODE DE PAIEMENT: {order.get_payment_method_display()}
Référence: {order.payment_reference or "N/A"}

ARTICLES COMMANDÉS:
{items_text}

SOUS-TOTAL: {int(order.total_price)} FCFA

ADRESSE DE LIVRAISON:
{order.shipping_address}

LOCALISATION DES PRODUITS:
{locations_text}

Nous traiterons votre commande dans les plus brefs délais.

L'équipe DJOKO SHOP
"""
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
            fail_silently=False,
        )
        
        order.receipt_sent = True
        order.save()
        
        print(f"Reçu envoyé à {order.user.email} pour la commande #{order.id}")
        
    except Exception as e:
        print(f"Erreur lors de l'envoi du reçu pour la commande #{order.id}: {e}")


@login_required
def profile(request):
    """Profil utilisateur avec préférences"""
    if request.method == 'POST':
        form = UserPreferencesForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour avec succès!')
            
    else:
        form = UserPreferencesForm(instance=request.user)
    
    return render(request, 'shop/profile.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Tableau de bord admin"""
    total_users = User.objects.count()
    total_vendors = User.objects.filter(role='vendor').count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    
    users = User.objects.all().order_by('-created_at')  # Ajout de la liste des utilisateurs
    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    
    context = {
        'total_users': total_users,
        'total_vendors': total_vendors,
        'total_products': total_products,
        'total_orders': total_orders,
        'recent_orders': recent_orders,
        'users': users,  # Ajout des utilisateurs au contexte
    }
    return render(request, 'shop/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_edit_user(request, user_id):
    """Modifier un utilisateur"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"L'utilisateur {user.username} a été modifié avec succès!")
            return redirect('admin_dashboard')
    else:
        form = AdminUserEditForm(instance=user)
    
    return render(request, 'shop/admin_edit_user.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def admin_delete_user(request, user_id):
    """Supprimer un utilisateur"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f"L'utilisateur {username} a été supprimé avec succès!")
    
    return redirect('admin_dashboard')



