from django.db import connection
from django.shortcuts import render
from django.db.models import Prefetch
from rest_framework import viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import SqlLexer
from sqlparse import format

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

    queryset = Brand.objects.all()  # Will collect all the brands from the brand table

    @extend_schema(responses=BrandSerializer)
    def list(self, request):
        serializer = BrandSerializer(self.queryset, many=True) #passing the collected data to our serializer
        return Response(serializer.data)
    
class ProductViewSet(viewsets.ViewSet):
    """
    A simple Viewset for viewing products
    """

    queryset = Product.objects.all().isactive()  # Will collect all the products from the product table
    
    lookup_field = "slug"

    def retrieve(self, request, slug=None):
        serializer = ProductSerializer(
            Product.objects.filter(slug=slug)
            .select_related("category", "brand")
            .prefetch_related(Prefetch("product_line__product_image")),
            many=True,
        )
        data = Response(serializer.data)

        q = list(connection.queries)
        print(len(q))
        for qs in q:
            sqlformatted = format(str(qs["sql"]), reindent=True)
            print(highlight(sqlformatted, SqlLexer(), TerminalFormatter()))

        return data

    @extend_schema(responses=ProductSerializer)
    def list(self, request, slug=None):
        serializer = ProductSerializer(self.queryset, many=True) #passing the collected data to our serializer

        return Response(serializer.data)
    
    @action(
        methods=["get"], 
        detail=False, 
        url_path=r"category/(?P<category>\w+)/all",
    )
    def list_product_by_category(self, request, category=None):
        """
        An endpoint to return products by categroy
        """
        serializer = ProductSerializer(self.queryset.filter(category__name=category), many=True) 
        return Response(serializer.data)