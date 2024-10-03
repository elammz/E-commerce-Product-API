from rest_framework import serializers
from .models import Brand, Category, Product, ProductLine, ProductImage


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
    
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        exclude = ("id", "productline")

class ProductLineSerializer(serializers.ModelSerializer):
    product_image = ProductImageSerializer(many=True)

    class Meta:
        model = ProductLine
        fields = (
            "price", 
            "stock_qty",
            "order",
            "product_image",
        )
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

