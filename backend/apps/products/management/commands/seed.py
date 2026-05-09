"""
Management command: seed
Crea datos iniciales para que la tienda funcione desde el primer arranque.
  - Superusuario admin
  - Configuración de tienda (StoreConfig singleton)
  - Categorías y productos de ejemplo con stock

Uso:
    python manage.py seed
    python manage.py seed --reset   # borra productos y vuelve a crearlos
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Carga datos iniciales: superusuario, configuración de tienda y productos de ejemplo.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina todos los productos y categorías antes de sembrar.',
        )

    def handle(self, *args, **options):
        # Importar aquí para evitar problemas de AppRegistry
        from apps.products.models import Category, Product, Stock
        from apps.store_config.models import StoreConfig

        self.stdout.write(self.style.MIGRATE_HEADING('\n🌱  Iniciando seed de datos...\n'))

        # ── 1. Superusuario ──────────────────────────────────────────────────
        admin_user = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        admin_pass = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin1234')
        admin_email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@licoreria.com')

        if not User.objects.filter(username=admin_user).exists():
            User.objects.create_superuser(admin_user, admin_email, admin_pass)
            self.stdout.write(self.style.SUCCESS(
                f'  ✅ Superusuario creado → usuario: {admin_user}  |  contraseña: {admin_pass}'
            ))
        else:
            self.stdout.write(f'  ℹ️  Superusuario "{admin_user}" ya existe, omitiendo.')

        # ── 2. StoreConfig (Singleton) ───────────────────────────────────────
        config, created = StoreConfig.objects.get_or_create(pk=1)
        if created:
            config.store_name = 'Licorería Virtual'
            config.environment = StoreConfig.Environment.STG
            config.iva_percentage = 15
            config.nuvei_app_code_client_stg = os.environ.get('NUVEI_APP_CODE_CLIENT_STG', 'TEBANSTG-EC-CLIENT')
            config.nuvei_app_key_client_stg  = os.environ.get('NUVEI_APP_KEY_CLIENT_STG', '')
            config.nuvei_app_code_server_stg = os.environ.get('NUVEI_APP_CODE_SERVER_STG', 'TEBANSTG-EC-SERVER')
            config.nuvei_app_key_server_stg  = os.environ.get('NUVEI_APP_KEY_SERVER_STG', '')
            config.success_url = 'http://localhost:5173/success'
            config.failure_url = 'http://localhost:5173/failure'
            config.pending_url = 'http://localhost:5173/pending'
            config.save()
            self.stdout.write(self.style.SUCCESS('  ✅ StoreConfig creada (ambiente: STG).'))
        else:
            self.stdout.write('  ℹ️  StoreConfig ya existe, omitiendo.')

        # ── 3. Reset opcional ────────────────────────────────────────────────
        if options['reset']:
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING('  ⚠️  Productos y categorías eliminados (--reset).'))

        # ── 4. Categorías ────────────────────────────────────────────────────
        categories_data = [
            {'name': 'Whisky',  'description': 'Whisky escocés, bourbon y blended.'},
            {'name': 'Ron',     'description': 'Ron blanco, añejo y oscuro.'},
            {'name': 'Vodka',   'description': 'Vodka premium y de importación.'},
            {'name': 'Vino',    'description': 'Vinos tintos, blancos y rosados.'},
            {'name': 'Cerveza', 'description': 'Cervezas nacionales e importadas.'},
            {'name': 'Gin',     'description': 'Gin artesanal y de importación.'},
        ]

        categories = {}
        for cat_data in categories_data:
            cat, _ = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description'], 'is_active': True}
            )
            categories[cat.name] = cat

        self.stdout.write(self.style.SUCCESS(f'  ✅ {len(categories)} categorías listas.'))

        # ── 5. Productos ─────────────────────────────────────────────────────
        products_data = [
            # Whisky
            {'category': 'Whisky', 'brand': 'Johnnie Walker', 'name': 'Black Label 12 años',
             'description': 'Blend escocés con notas de frutos secos y especias.', 'price': '42.50',
             'alcohol_content': '40.00', 'volume_ml': 750, 'stock': 25},
            {'category': 'Whisky', 'brand': 'Jack Daniel\'s', 'name': 'Old No. 7',
             'description': 'Famoso Tennessee Whiskey con sabor suave y ahumado.', 'price': '35.00',
             'alcohol_content': '40.00', 'volume_ml': 750, 'stock': 30},
            {'category': 'Whisky', 'brand': 'Chivas Regal', 'name': '12 años',
             'description': 'Blended Scotch con carácter suave y afrutado.', 'price': '38.00',
             'alcohol_content': '40.00', 'volume_ml': 750, 'stock': 20},

            # Ron
            {'category': 'Ron', 'brand': 'Barceló', 'name': 'Imperial Añejo',
             'description': 'Ron premium dominicano envejecido 10 años.', 'price': '28.00',
             'alcohol_content': '38.00', 'volume_ml': 750, 'stock': 40},
            {'category': 'Ron', 'brand': 'Havana Club', 'name': '7 años',
             'description': 'Ron cubano añejo con toques de vainilla y madera.', 'price': '22.00',
             'alcohol_content': '40.00', 'volume_ml': 750, 'stock': 35},

            # Vodka
            {'category': 'Vodka', 'brand': 'Absolut', 'name': 'Original',
             'description': 'Vodka sueco premium, limpio y versátil.', 'price': '20.00',
             'alcohol_content': '40.00', 'volume_ml': 750, 'stock': 50},
            {'category': 'Vodka', 'brand': 'Grey Goose', 'name': 'Original',
             'description': 'Vodka francés ultra-premium destilado con trigo brie.', 'price': '45.00',
             'alcohol_content': '40.00', 'volume_ml': 750, 'stock': 15},

            # Vino
            {'category': 'Vino', 'brand': 'Concha y Toro', 'name': 'Casillero del Diablo Cabernet',
             'description': 'Vino tinto chileno con notas de cereza y chocolate.', 'price': '12.00',
             'alcohol_content': '13.50', 'volume_ml': 750, 'stock': 60},
            {'category': 'Vino', 'brand': 'Santa Rita', 'name': '120 Sauvignon Blanc',
             'description': 'Vino blanco fresco y afrutado, ideal para mariscos.', 'price': '10.00',
             'alcohol_content': '12.50', 'volume_ml': 750, 'stock': 45},

            # Cerveza
            {'category': 'Cerveza', 'brand': 'Corona', 'name': 'Extra Lager',
             'description': 'Cerveza mexicana ligera y refrescante.', 'price': '2.50',
             'alcohol_content': '4.50', 'volume_ml': 355, 'stock': 120},
            {'category': 'Cerveza', 'brand': 'Pilsener', 'name': 'Clásica Ecuador',
             'description': 'La cerveza nacional ecuatoriana por excelencia.', 'price': '1.50',
             'alcohol_content': '4.00', 'volume_ml': 330, 'stock': 200},

            # Gin
            {'category': 'Gin', 'brand': 'Bombay Sapphire', 'name': 'London Dry Gin',
             'description': 'Gin británico con 10 botánicos exóticos.', 'price': '32.00',
             'alcohol_content': '47.00', 'volume_ml': 750, 'stock': 20},
            {'category': 'Gin', 'brand': 'Tanqueray', 'name': 'London Dry',
             'description': 'Gin clásico con enebro y notas cítricas.', 'price': '28.00',
             'alcohol_content': '43.10', 'volume_ml': 750, 'stock': 18},
        ]

        created_count = 0
        for p_data in products_data:
            cat = categories[p_data['category']]
            product, created = Product.objects.get_or_create(
                brand=p_data['brand'],
                name=p_data['name'],
                defaults={
                    'category': cat,
                    'description': p_data['description'],
                    'price': p_data['price'],
                    'alcohol_content': p_data['alcohol_content'],
                    'volume_ml': p_data['volume_ml'],
                    'is_active': True,
                }
            )
            # Crear o actualizar stock
            stock_obj, _ = Stock.objects.get_or_create(product=product)
            if stock_obj.quantity == 0:
                stock_obj.quantity = p_data['stock']
                stock_obj.min_quantity = 5
                stock_obj.save()

            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'  ✅ {created_count} producto(s) creados ({len(products_data) - created_count} ya existían).'
        ))

        self.stdout.write(self.style.SUCCESS('\n🎉  Seed completado. La tienda está lista.\n'))
        self.stdout.write(f'  → Admin:    http://localhost:8000/admin')
        self.stdout.write(f'  → Tienda:   http://localhost:5173')
        self.stdout.write(f'  → Usuario:  {admin_user}  /  Contraseña: {admin_pass}\n')
