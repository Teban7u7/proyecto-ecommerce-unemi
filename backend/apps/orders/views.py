from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.conf import settings
import requests

from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer
from apps.products.models import Product
from apps.store_config.models import StoreConfig


class OrderViewSet(viewsets.ModelViewSet):
    """Order management ViewSet."""
    queryset = Order.objects.prefetch_related('items', 'items__product').all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'update', 'partial_update', 'destroy', 'change_status'):
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]  # create and webhook are public

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Get store config for tax and environment
        config = StoreConfig.get_config()

        # Create order
        order = Order.objects.create(
            customer_name=data['customer_name'],
            customer_phone=data['customer_phone'],
            customer_email=data['customer_email'],
            tax_percentage=config.iva_percentage,
            installments_type=data.get('installments_type', 0),
            environment=config.environment,
        )

        # Create order items and deduct stock
        for item_data in data['items']:
            product = Product.objects.select_related('stock').get(id=item_data['product_id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                unit_price=product.price,
            )
            # Deduct stock
            product.stock.quantity -= item_data['quantity']
            product.stock.save()

        # Calculate totals with IVA
        order.calculate_totals()
        order.save()

        # Call Node.js payment service
        creds = config.get_active_credentials()
        payment_method = data.get('payment_method', 'linktopay')
        node_response_data = None
        
        try:
            payment_payload = {
                'app_code': creds['app_code_server'],
                'app_key': creds['app_key_server'],
                'noccapi_url': creds['noccapi_url'],
                'ccapi_url': creds['ccapi_url'],
                'user': {
                    'id': str(order.id),
                    'email': order.customer_email or 'esteban.alava@nuvei.com',
                    'name': order.customer_name.split()[0] if ' ' in order.customer_name else order.customer_name,
                    'last_name': order.customer_name.split(' ', 1)[1] if ' ' in order.customer_name else 'N/A',
                },
                'order': {
                    'dev_reference': f'ORD-{order.id}',
                    'description': f'Pedido Licorería',
                    'amount': round(float(order.total), 2),
                    'vat': round(float(order.vat_amount), 2),
                    'taxable_amount': round(float(order.subtotal), 2),
                    'tax_percentage': order.tax_percentage,
                    'installments_type': order.installments_type,
                    'currency': 'USD'
                }
            }

            if payment_method == 'checkout':
                payment_payload['conf'] = config.get_checkout_conf()
                endpoint = f"{settings.PAYMENT_SERVICE_URL}/api/payments/checkout-reference"
            else:
                payment_payload['configuration'] = {
                    'partial_payment': False,
                    'expiration_days': 1,
                    'allowed_payment_methods': ['All'],
                    'success_url': config.success_url or 'http://localhost:5173/success',
                    'failure_url': config.failure_url or 'http://localhost:5173/failure',
                    'pending_url': config.pending_url or 'http://localhost:5173/pending',
                    'review_url': config.success_url or 'http://localhost:5173/review',
                }
                if config.webhook_url:
                    payment_payload['configuration']['webhook_url'] = config.webhook_url
                    
                endpoint = f"{settings.PAYMENT_SERVICE_URL}/api/payments/link-to-pay"
            
            response = requests.post(endpoint, json=payment_payload, timeout=10)
            
            if response.status_code == 200:
                node_response_data = response.json()
                print("NODE JS RESPONSE:", node_response_data, flush=True)
                if node_response_data.get('success') or (payment_method == 'checkout' and 'reference' in node_response_data):
                    if payment_method == 'linktopay':
                        order.payment_url = node_response_data['data']['payment']['payment_url']
                        order.ltp_id = node_response_data['data']['order']['id']
                    else:
                        order.nuvei_transaction_id = node_response_data['reference']
                    
                    order.status = Order.Status.PAYMENT_SENT
                    order.save(update_fields=['payment_url', 'ltp_id', 'nuvei_transaction_id', 'status'])
                else:
                    return Response({"error": "Error de Nuvei", "details": node_response_data}, status=status.HTTP_400_BAD_REQUEST)
            else:
                print(f"Node.js error: {response.status_code} - {response.text}", flush=True)
                return Response({"error": "Error del microservicio de pago", "details": response.text}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error calling payment service: {e}", flush=True)
            return Response({"error": "Error interno al contactar al servicio de pago", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response_data = OrderSerializer(order).data
        response_data['nuvei_response'] = node_response_data

        return Response(
            response_data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['put'], url_path='status')
    def change_status(self, request, pk=None):
        """Change order status (admin only)."""
        order = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(Order.Status.choices):
            return Response(
                {'error': f'Estado inválido. Opciones: {list(dict(Order.Status.choices).keys())}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])
        return Response(OrderSerializer(order).data)

    @action(detail=False, methods=['post'], url_path='webhook')
    def webhook(self, request):
        """Receive callback from Nuvei."""
        data = request.data
        print(f"WEBHOOK RECEIVED: {data}", flush=True)
        
        # Extracción segura de la data del payload de Nuvei
        transaction_data = data.get('transaction', {})
        dev_reference = transaction_data.get('dev_reference') or data.get('dev_reference')
        
        if not dev_reference:
            return Response({'error': 'No dev_reference provided'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            order = Order.objects.get(dev_reference=dev_reference)
            
            # Extraer status y código de autorización
            tx_status = transaction_data.get('status') or data.get('status')
            auth_code = transaction_data.get('authorization_code') or data.get('authorization_code', '')
            
            # Mapear estados de Nuvei a nuestros PaymentStatus
            status_mapping = {
                'success': Order.PaymentStatus.APPROVED,
                'approved': Order.PaymentStatus.APPROVED,
                'pending': Order.PaymentStatus.PENDING,
                'rejected': Order.PaymentStatus.REJECTED,
                'failure': Order.PaymentStatus.REJECTED,
            }
            
            mapped_status = status_mapping.get(str(tx_status).lower(), Order.PaymentStatus.PENDING)
            order.payment_status = mapped_status
            
            if auth_code:
                order.authorization_code = auth_code
                
            if mapped_status == Order.PaymentStatus.APPROVED:
                order.status = Order.Status.PAID
                # TODO: Trigger Email notification here
                print(f"✅ ¡PAGO APROBADO! Orden {order.dev_reference} (Auth: {auth_code})", flush=True)
            else:
                print(f"❌ PAGO DENEGADO/PENDIENTE: Orden {order.dev_reference} - Estado: {mapped_status}", flush=True)
                
            order.save()
            return Response({'status': 'ok'})
            
        except Order.DoesNotExist:
            print(f"WEBHOOK ERROR: Order {dev_reference} not found", flush=True)
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
