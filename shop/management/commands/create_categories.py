from django.core.management.base import BaseCommand
from shop.models import Category


class Command(BaseCommand):
    help = 'Créer les catégories par défaut'

    def handle(self, *args, **kwargs):
        categories = [
            'Mode & Vêtements',
            'Chaussures',
            'Accessoires',
            'Électronique',
            'Maison & Décoration',
            'Beauté & Santé',
            'Sport & Fitness',
            'Livres',
            'Jouets & Jeux',
            'Autres'
        ]
        
        for cat_name in categories:
            category, created = Category.objects.get_or_create(name=cat_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Catégorie "{cat_name}" créée'))
            else:
                self.stdout.write(self.style.WARNING(f'Catégorie "{cat_name}" existe déjà'))
        
        self.stdout.write(self.style.SUCCESS('Catégories créées avec succès!'))

