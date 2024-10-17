from rest_framework import serializers
from .models import Brand, Category, Product, ProductLine, ProductImage, Attribute, AttributeValue
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


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
        fields = ('alternative_text', 'url', 'order')
    
class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ("name", "id")


class AttributeValueSerializer(serializers.ModelSerializer):
    attribute = AttributeSerializer(many=False)

    class Meta:
        model = AttributeValue
        fields = (
            "attribute",
            "attribute_value",
        )

class ProductLineSerializer(serializers.ModelSerializer):
    product_image = ProductImageSerializer(many=True)

    class Meta:
        model = ProductLine
        fields = (
            "price", 
            "stock_qty",
            "order",
            "product_image",
            "attribute_value",
        )
        # fields = "__all__"
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        av_data = data.pop("attribute_value", [])
        attr_values = {}

        if isinstance(av_data, list):
            # Fetch the AttributeValue instances based on IDs
            attribute_values = AttributeValue.objects.filter(id__in=av_data).select_related('attribute')

            for item in attribute_values:
                attr_values[item.attribute.id] = item.attribute_value

        data.update({"specification": attr_values})

        return data

class ProductSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source="brand.name")
    category_name = serializers.CharField(source="category.name")
    product_line = ProductLineSerializer(many=True)
    attribute = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "name", 
            "slug", 
            "description", 
            "brand_name", 
            "category_name", 
            "product_line",
            "attribute",
        )
        # fields = "__all__"
    
    def get_attribute(self, obj):
        attribute = Attribute.objects.filter(product_type_attribute__product__id=obj.id)
        return AttributeSerializer(attribute, many=True).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        av_data = data.pop("attribute")
        attr_values = {}

        for key in av_data:
            attr_values.update({key["id"]: key["name"]})
            
        data.update({"specification_type": attr_values})

        return data

