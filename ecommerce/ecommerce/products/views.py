from django.db.models import Prefetch
from rest_framework import viewsets, generics, permissions, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated

from .models import Category, Brand, Product
from .serializers import CategorySerializer, BrandSerializer, ProductSerializer, UserSerializer


# User Registration and Update Views
class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer


class UpdateUserView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


# Pagination class
class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# Filter for products
class ProductFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    in_stock = django_filters.BooleanFilter(field_name="stock_qty", lookup_expr='gt', method='filter_in_stock')

    class Meta:
        model = Product
        fields = ['category', 'price_min', 'price_max', 'in_stock']

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock_qty__gt=0)
        return queryset


# Category ViewSet
class CategoryViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for viewing categories.
    """
    queryset = Category.objects.all()

    @extend_schema(responses=CategorySerializer)
    def list(self, request):
        serializer = CategorySerializer(self.queryset, many=True)
        return Response(serializer.data)


# Brand ViewSet
class BrandViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for viewing brands.
    """
    queryset = Brand.objects.all()

    @extend_schema(responses=BrandSerializer)
    def list(self, request):
        serializer = BrandSerializer(self.queryset, many=True)
        return Response(serializer.data)


# Product ViewSet
class ProductViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and managing products.
    """
    queryset = Product.objects.all().filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]  # Restrict to authenticated users
    pagination_class = ProductPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'category__name']
    filterset_class = ProductFilter
    lookup_field = "slug"

    def retrieve(self, request, slug=None):
        """
        Retrieve a single product by slug.
        """
        try:
            product = Product.objects.filter(slug=slug).select_related("category", "brand").prefetch_related(
                Prefetch("product_line__product_image"),
                Prefetch("product_line__attribute_value__attribute")
            ).first()

            if not product:
                return Response({"detail": "Not found."}, status=404)

            serializer = self.serializer_class(product)
            return Response(serializer.data)

        except Exception as e:
            return Response({"detail": str(e)}, status=500)

    @action(
        methods=["get"],
        detail=False,
        url_path=r"category/(?P<category>[\w-]+)",
    )
    def list_product_by_category_slug(self, request, category=None):
        """
        List products by category slug.
        """
        products = self.queryset.filter(category__slug=category)
        serializer = self.serializer_class(products, many=True)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """
        List products with pagination and filtering.
        """
        products = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
