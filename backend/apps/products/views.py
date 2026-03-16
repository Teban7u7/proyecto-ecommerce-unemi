from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Category, Product, Stock
from .serializers import (
    CategorySerializer, ProductSerializer,
    ProductCreateSerializer, StockSerializer,
)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow read-only for anyone, write for admin users only."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_staff or getattr(request.user, 'role', '') == 'admin'
        )


class CategoryViewSet(viewsets.ModelViewSet):
    """CRUD for product categories."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    search_fields = ['name']

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            qs = qs.filter(is_active=True)
        return qs


class ProductViewSet(viewsets.ModelViewSet):
    """CRUD for products."""
    queryset = Product.objects.select_related('category', 'stock').all()
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['name', 'brand', 'description']
    filterset_fields = ['category', 'is_active', 'brand']
    ordering_fields = ['price', 'name', 'created_at']

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return ProductCreateSerializer
        return ProductSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            qs = qs.filter(is_active=True)
        return qs


class StockViewSet(viewsets.ModelViewSet):
    """Manage product stock. Admin only."""
    queryset = Stock.objects.select_related('product').all()
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'head', 'options']
