from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
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

    queryset = Product.objects.all()  # Will collect all the products from the product table

    @extend_schema(responses=ProductSerializer)
    def list(self, request):
        serializer = ProductSerializer(self.queryset, many=True) #passing the collected data to our serializer
        return Response(serializer.data)