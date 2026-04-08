from rest_framework import serializers
from .models import Order, OrderItem
from apps.products.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'unit_price', 'subtotal')
        read_only_fields = ('id', 'subtotal')


class OrderItemCreateSerializer(serializers.Serializer):
    """Simplified serializer for creating order items."""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'customer_name', 'customer_phone', 'customer_email',
            'status', 'subtotal', 'vat_amount', 'tax_percentage', 'total',
            'installments_type', 'payment_url', 'payment_status',
            'nuvei_transaction_id', 'dev_reference', 'ltp_id', 'environment',
            'items', 'created_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'subtotal', 'vat_amount', 'total', 'payment_url',
            'payment_status', 'nuvei_transaction_id', 'dev_reference',
            'ltp_id', 'environment', 'created_at', 'updated_at',
        )


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating a new order with items."""
    customer_name = serializers.CharField(max_length=200)
    customer_phone = serializers.CharField(max_length=20)
    customer_email = serializers.EmailField()
    items = OrderItemCreateSerializer(many=True)
    payment_method = serializers.ChoiceField(
        choices=[('linktopay', 'Link to Pay'), ('checkout', 'Checkout Modal')],
        default='linktopay'
    )
    installments_type = serializers.ChoiceField(
        choices=Order.InstallmentsType.choices,
        default=Order.InstallmentsType.CORRIENTE,
    )

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError('La orden debe tener al menos un producto.')
        for item in items:
            try:
                product = Product.objects.select_related('stock').get(
                    id=item['product_id'], is_active=True
                )
            except Product.DoesNotExist:
                raise serializers.ValidationError(
                    f'Producto con ID {item["product_id"]} no encontrado o inactivo.'
                )
            if not hasattr(product, 'stock') or product.stock.quantity < item['quantity']:
                raise serializers.ValidationError(
                    f'Stock insuficiente para {product.name}. '
                    f'Disponible: {getattr(product.stock, "quantity", 0)}'
                )
        return items
