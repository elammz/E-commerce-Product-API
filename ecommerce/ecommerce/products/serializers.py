from rest_framework import serializers
from .models import Brand, Category, Product, ProductLine


class CategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="name")
    class Meta:
        model = Category
        # exclude = ("id",)
        fields = ["category_name",]  
        # Will only include the name and display, we also changed the display name from 'name' to 'category_name'

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        exclude = ("id",)   # excludes the id section and display the rest
        # fields = "__all__"

class ProductLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductLine
        exclude = ("id", "is_active", "Product")
        # fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source="brand.name")
    category_name = serializers.CharField(source="category.name")
    product_line = ProductLineSerializer(many=True)

    class Meta:
        model = Product
        fields = (
            "name", 
            "slug", 
            "description", 
            "brand_name", 
            "category_name", 
            "product_line",
        )
        # fields = "__all__"

