from django.db import connection
from django.db.models import Prefetch
from rest_framework import viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import SqlLexer
from sqlparse import format
from rest_framework import status

from .models import Category, Brand, Product
from .serializers import CategorySerializer, BrandSerializer, ProductSerializer


class CategoryViewSet(viewsets.ViewSet):
    """
    A simple Viewset for viewing catagories
    """

    queryset = Category.objects.all()  # Will collect all the categories from the category table

    @extend_schema(responses=CategorySerializer)
    def list(self, request):
        serializer = CategorySerializer(self.queryset, many=True) #passing the collected data to our serializer
        return Response(serializer.data)

class BrandViewSet(viewsets.ViewSet):
    """
    A simple Viewset for viewing brands
    """

    queryset = Brand.objects.all()  # Collect all the brands from the brand table

    @extend_schema(responses=BrandSerializer)
    def list(self, request):
        serializer = BrandSerializer(self.queryset, many=True) #passing the collected data to our serializer
        return Response(serializer.data)

class ProductViewSet(viewsets.ViewSet):
    """
    A simple Viewset for viewing products
    """
    queryset = Product.objects.all().filter(is_active=True)  # Ensure you're filtering for active products
    serializer_class = ProductSerializer 
    lookup_field = "slug"

    def retrieve(self, request, slug=None):
        try:
            product = Product.objects.filter(slug=slug).select_related("category", "brand").prefetch_related(
                Prefetch("product_line__product_image"),
                Prefetch("product_line__attribute_value__attribute")
            ).first()  # Use first() to get a single instance

            if not product:
                return Response({"detail": "Not found."}, status=404)

            serializer = self.serializer_class(product)  # Pass the single instance to the serializer
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
        An endpoint to return products by category
        """
        products = self.queryset.filter(category__slug=category)
        serializer = self.serializer_class(products, many=True)  # Pass filtered queryset to the serializer
        return Response(serializer.data)

    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)  # Pass the queryset to the serializer
        return Response(serializer.data)


# class ProductViewSet(viewsets.ViewSet):
#     """
#     A simple Viewset for viewing products
#     """

#     queryset = Product.objects.all().isactive()  # Will collect all active products from the product table
    
#     lookup_field = "slug"

#     def retrieve(self, request, slug=None):
#         serializer = ProductSerializer(
#             Product.objects.filter(slug=slug)
#             .select_related("category", "brand")
#             .prefetch_related(Prefetch("product_line__product_image"))
#             .prefetch_related(Prefetch("product_line__attribute_value__attribute"))
#         )
#         data = Response(serializer.data)

#         return data

#     @extend_schema(responses=ProductSerializer)
#     def list(self, request):
#         serializer = ProductSerializer(self.queryset, many=True) #passing the collected data to our serializer

#         return Response(serializer.data)
    
#     @action(
#         methods=["get"], 
#         detail=False, 
#         url_path=r"category/(?P<category>[\w-]+)",
#     )
#     def list_product_by_category_slug(self, request, slug=None):
#         """
#         An endpoint to return products by categroy
#         """
#         serializer = ProductSerializer(self.queryset.filter(category__slug=slug), many=True) 

#         return Response(serializer.data)