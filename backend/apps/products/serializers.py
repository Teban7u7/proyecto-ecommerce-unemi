from rest_framework import serializers
from .models import Category, Product, Stock


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'image',
                  'is_active', 'product_count', 'created_at')
        read_only_fields = ('id', 'slug', 'created_at')

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class StockSerializer(serializers.ModelSerializer):
    is_low_stock = serializers.BooleanField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Stock
        fields = ('id', 'product', 'product_name', 'quantity', 'min_quantity',
                  'is_low_stock', 'is_available', 'last_restocked', 'updated_at')
        read_only_fields = ('id', 'updated_at')


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    stock_quantity = serializers.IntegerField(source='stock.quantity', read_only=True, default=0)
    is_available = serializers.BooleanField(source='stock.is_available', read_only=True, default=False)

    class Meta:
        model = Product
        fields = ('id', 'category', 'category_name', 'name', 'slug', 'description',
                  'price', 'image', 'alcohol_content', 'volume_ml', 'brand',
                  'is_active', 'stock_quantity', 'is_available',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')


class ProductCreateSerializer(serializers.ModelSerializer):
    initial_stock = serializers.IntegerField(write_only=True, required=False, default=0)

    class Meta:
        model = Product
        fields = ('id', 'category', 'name', 'description', 'price', 'image',
                  'alcohol_content', 'volume_ml', 'brand', 'is_active', 'initial_stock')

    def create(self, validated_data):
        initial_stock = validated_data.pop('initial_stock', 0)
        product = super().create(validated_data)
        Stock.objects.create(product=product, quantity=initial_stock)
        return product
