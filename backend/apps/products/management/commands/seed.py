"""
Management command: seed
Crea datos iniciales para que la tienda funcione desde el primer arranque.
  - Superusuario admin
  - Configuración de tienda (StoreConfig singleton)
  - Categorías y productos de ejemplo con stock e imágenes

Uso:
    python manage.py seed
    python manage.py seed --reset   # borra productos y vuelve a crearlos
"""
import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.files import File
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

# Directorio de imágenes estáticas de productos (frontend/public/images/products)
IMAGES_SOURCE_DIR = Path(settings.BASE_DIR).parent / 'frontend' / 'public' / 'images' / 'products'


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

        self.stdout.write(self.style.MIGRATE_HEADING('\n[SEED] Iniciando seed de datos...\n'))

        # ── 1. Superusuario ──────────────────────────────────────────────────
        admin_user = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        admin_pass = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin1234')
        admin_email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@licoreria.com')

        if not User.objects.filter(username=admin_user).exists():
            User.objects.create_superuser(admin_user, admin_email, admin_pass)
            self.stdout.write(self.style.SUCCESS(
                f'  [OK] Superusuario creado -> usuario: {admin_user}  |  contrasena: {admin_pass}'
            ))
        else:
            self.stdout.write(f'  [INFO] Superusuario "{admin_user}" ya existe, omitiendo.')

        # ── 2. StoreConfig (Singleton) ───────────────────────────────────────
        config, created = StoreConfig.objects.get_or_create(pk=1)
        if created:
            config.store_name = 'NightDrop Licorería'
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
            self.stdout.write(self.style.SUCCESS('  [OK] StoreConfig creada (ambiente: STG).'))
        else:
            self.stdout.write('  [INFO] StoreConfig ya existe, omitiendo.')

        # ── 3. Reset opcional ────────────────────────────────────────────────
        if options['reset']:
            from apps.orders.models import Order, OrderItem
            OrderItem.objects.all().delete()
            Order.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()
            # Limpiar media/products
            media_products = settings.MEDIA_ROOT / 'products'
            if media_products.exists():
                shutil.rmtree(media_products)
                media_products.mkdir(parents=True, exist_ok=True)
            self.stdout.write(self.style.WARNING('  [WARN] Ordenes, productos y categorias eliminados (--reset).'))

        # ── 4. Categorías ────────────────────────────────────────────────────
        categories_data = [
            {'name': 'Whisky',   'description': 'Whisky escocés, bourbon y blended de las mejores destilerías.'},
            {'name': 'Ron',      'description': 'Ron blanco, añejo y oscuro de origen caribeño y latinoamericano.'},
            {'name': 'Vodka',    'description': 'Vodka premium y ultra-premium de importación.'},
            {'name': 'Vino',     'description': 'Vinos tintos, blancos y rosados de las mejores cepas.'},
            {'name': 'Cerveza',  'description': 'Cervezas artesanales, nacionales e importadas.'},
            {'name': 'Gin',      'description': 'Gin artesanal y de importación con botánicos selectos.'},
            {'name': 'Especial', 'description': 'Ediciones limitadas y botellas de colección.'},
        ]

        categories = {}
        for cat_data in categories_data:
            cat, _ = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description'], 'is_active': True}
            )
            categories[cat.name] = cat

        self.stdout.write(self.style.SUCCESS(f'  [OK] {len(categories)} categorias listas.'))

        # ── 5. Productos con imágenes ────────────────────────────────────────
        products_data = [
            # Whisky
            {'category': 'Whisky', 'brand': 'Highland Reserve', 'name': 'Black Label 12 Años',
             'description': 'Blend escocés premium con notas de frutos secos, especias y un toque ahumado. Envejecido 12 años en barricas de roble.',
             'price': '42.50', 'alcohol_content': '40.00', 'volume_ml': 750, 'stock': 25,
             'image': 'whisky_black_label.png'},

            {'category': 'Whisky', 'brand': 'Tennessee Oak', 'name': 'Classic No. 7',
             'description': 'Whiskey americano con carácter suave y ahumado, filtrado a través de carbón de arce. Ideal para cócteles y solo.',
             'price': '35.00', 'alcohol_content': '40.00', 'volume_ml': 750, 'stock': 30,
             'image': 'whisky_tennessee.png'},

            {'category': 'Whisky', 'brand': 'Royal Glen', 'name': 'Reserva 12 Años',
             'description': 'Blended Scotch con carácter suave y afrutado. Notas de miel, manzana y un final cremoso.',
             'price': '38.00', 'alcohol_content': '40.00', 'volume_ml': 750, 'stock': 20,
             'image': 'whisky_12_years.png'},

            # Ron
            {'category': 'Ron', 'brand': 'Caribeño Dorado', 'name': 'Imperial Añejo 10 Años',
             'description': 'Ron premium caribeño envejecido 10 años en barricas de roble americano. Sabor suave con notas de vainilla y caramelo.',
             'price': '28.00', 'alcohol_content': '38.00', 'volume_ml': 750, 'stock': 40,
             'image': 'ron_imperial.png'},

            {'category': 'Ron', 'brand': 'Isla Dorada', 'name': 'Añejo 7 Años',
             'description': 'Ron cubano de tradición centenaria, envejecido 7 años. Toques de vainilla, madera y cacao.',
             'price': '22.00', 'alcohol_content': '40.00', 'volume_ml': 750, 'stock': 35,
             'image': 'ron_7_years.png'},

            # Vodka
            {'category': 'Vodka', 'brand': 'Nordic Frost', 'name': 'Original Premium',
             'description': 'Vodka nórdico premium, destilado con trigo seleccionado. Limpio, versátil y extraordinariamente suave.',
             'price': '20.00', 'alcohol_content': '40.00', 'volume_ml': 750, 'stock': 50,
             'image': 'vodka_premium.png'},

            {'category': 'Vodka', 'brand': 'Château Blanc', 'name': 'Ultra Premium',
             'description': 'Vodka francés ultra-premium destilado con trigo de la región de Brie. Suavidad y pureza excepcional.',
             'price': '45.00', 'alcohol_content': '40.00', 'volume_ml': 750, 'stock': 15,
             'image': 'vodka_ultra_premium.png'},

            # Vino
            {'category': 'Vino', 'brand': 'Valle Central', 'name': 'Cabernet Sauvignon Reserva',
             'description': 'Vino tinto chileno con intensas notas de cereza negra, chocolate y especias. Cuerpo medio-alto.',
             'price': '12.00', 'alcohol_content': '13.50', 'volume_ml': 750, 'stock': 60,
             'image': 'vino_tinto_cabernet.png'},

            {'category': 'Vino', 'brand': 'Costa Pacífico', 'name': 'Sauvignon Blanc Reserva',
             'description': 'Vino blanco fresco y afrutado con notas cítricas y florales. Ideal para mariscos y ensaladas.',
             'price': '10.00', 'alcohol_content': '12.50', 'volume_ml': 750, 'stock': 45,
             'image': 'vino_blanco_sauvignon.png'},

            # Cerveza
            {'category': 'Cerveza', 'brand': 'Sol Dorado', 'name': 'Lager Premium',
             'description': 'Cerveza lager ligera y refrescante de estilo mexicano. Perfecta para el clima ecuatoriano.',
             'price': '2.50', 'alcohol_content': '4.50', 'volume_ml': 355, 'stock': 120,
             'image': 'cerveza_lager_mexicana.png'},

            {'category': 'Cerveza', 'brand': 'Montaña', 'name': 'Pilsner Clásica',
             'description': 'Cerveza pilsner artesanal ecuatoriana. Sabor auténtico con lúpulo seleccionado.',
             'price': '1.50', 'alcohol_content': '4.00', 'volume_ml': 330, 'stock': 200,
             'image': 'cerveza_ecuatoriana.png'},

            # Gin
            {'category': 'Gin', 'brand': 'Sapphire Bay', 'name': 'London Dry Gin',
             'description': 'Gin británico artesanal con 10 botánicos exóticos cuidadosamente seleccionados. Notas de enebro y cítricos.',
             'price': '32.00', 'alcohol_content': '47.00', 'volume_ml': 750, 'stock': 20,
             'image': 'gin_london_dry.png'},

            {'category': 'Gin', 'brand': 'Green Valley', 'name': 'London Dry Clásico',
             'description': 'Gin clásico de destilación cuádruple con enebro, cilantro y notas cítricas intensas.',
             'price': '28.00', 'alcohol_content': '43.10', 'volume_ml': 750, 'stock': 18,
             'image': 'gin_classic.png'},

            # ✨ Edición Especial
            {'category': 'Especial', 'brand': 'Nocturna', 'name': 'Edición Limitada Mystic',
             'description': 'Licor artesanal de edición limitada con infusión de frutos del bosque y especias ancestrales. Solo para conocedores.',
             'price': '19.00', 'alcohol_content': '20.00', 'volume_ml': 500, 'stock': 1,
             'image': 'licor_especial.png'},
        ]

        created_count = 0
        images_assigned = 0
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

            # Asignar imagen si existe y el producto no tiene una
            if p_data.get('image') and not product.image:
                image_path = IMAGES_SOURCE_DIR / p_data['image']
                if image_path.exists():
                    with open(image_path, 'rb') as img_file:
                        product.image.save(p_data['image'], File(img_file), save=True)
                    images_assigned += 1
                else:
                    self.stdout.write(self.style.WARNING(
                        f'  [WARN] Imagen no encontrada: {image_path}'
                    ))

            # Crear o actualizar stock
            stock_obj, _ = Stock.objects.get_or_create(product=product)
            if stock_obj.quantity == 0:
                stock_obj.quantity = p_data['stock']
                stock_obj.min_quantity = 5
                stock_obj.save()

            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'  [OK] {created_count} producto(s) creados ({len(products_data) - created_count} ya existian).'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'  [IMG] {images_assigned} imagen(es) asignadas a productos.'
        ))

        self.stdout.write(self.style.SUCCESS('\n[DONE] Seed completado. La tienda esta lista.\n'))
        self.stdout.write(f'  -> Admin:    http://localhost:8000/admin')
        self.stdout.write(f'  -> Tienda:   http://localhost:5173')
        self.stdout.write(f'  -> Usuario:  {admin_user}  /  Password: {admin_pass}\n')
