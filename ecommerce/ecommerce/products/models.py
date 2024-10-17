from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from .fields import OrderField
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)

    # Add related_name to avoid conflicts with auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  # Set a custom related name
        blank=True,
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',  # Set a custom related name
        blank=True,
        help_text='Specific permissions for this user.'
    )

    def __str__(self):
        return self.username

class ActiveQueryset(models.QuerySet):
    def isactive(self):
        return self.filter(is_active=True)

class Category(MPTTModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=255)
    parent = TreeForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    objects = ActiveQueryset.as_manager()

    class MPTTMeta:
        order_insertion_by = ("name")

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    objects = ActiveQueryset.as_manager()

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255)
    description =models.TextField(blank=True)
    is_digital = models.BooleanField(default=False) # Defines if the product is shippable or to download
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE) #If the Brand is deleted we won't have Product (it all will be deleted)
    category = TreeForeignKey(
        "Category", on_delete=models.SET_NULL, null=True, blank=True
    ) # null and blank defines that some products may not be part of the category  
    is_active = models.BooleanField(default=True) # This will allow us to keep the product active or not
    product_type = models.ForeignKey("ProductType", on_delete=models.PROTECT, related_name="product")
    objects = ActiveQueryset.as_manager()

    def __str__(self):
        return self.name

class Attribute(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    attribute_value = models.CharField(max_length=100)
    attribute = models.ForeignKey(
        Attribute, on_delete=models.CASCADE, related_name="attribute_value"
    )

    def __str__(self):
        return f"{self.attribute.name}-{self.attribute_value}"


class ProductLineAttributeValue(models.Model):
    attribute_value = models.ForeignKey(
        AttributeValue,
        on_delete=models.CASCADE,
        related_name="product_attribute_value_av",
    )
    product_line = models.ForeignKey(
        "ProductLine",
        on_delete=models.CASCADE,
        related_name="product_attribute_value_pl",
    )

    class Meta:
        unique_together = ("attribute_value", "product_line")

    def clean(self):
        qs = (
            ProductLineAttributeValue.objects.filter(
                attribute_value=self.attribute_value
            )
            .filter(product_line=self.product_line)
            .exists()
        )

        if not qs:
            iqs = Attribute.objects.filter(
                attribute_value__product_line_attribute_value=self.product_line
            ).values_list("pk", flat=True)

            if self.attribute_value.attribute.id in list(iqs):
                raise ValidationError("Duplicate attribute exists")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(ProductLineAttributeValue, self).save(*args, **kwargs)

class ProductLine(models.Model):
    price = models.DecimalField(decimal_places=2, max_digits=10)
    sku = models.CharField(max_length=100)
    stock_qty = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_line")
    is_active = models.BooleanField(default=False) # This will allow us to keep the product active or not
    order = OrderField(unique_for_field="product", blank=True)
    attribute_value = models.ManyToManyField(
        AttributeValue, 
        through="ProductLineAttributeValue", 
        related_name="product_line_attribute_value",
    )
    objects = ActiveQueryset.as_manager()

    def clean(self):
        qs = ProductLine.objects.filter(product=self.product)
        for obj in qs:
            if self.id != obj.id and self.order == obj.order:
                raise ValidationError("Duplicate value.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(ProductLine, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.sku)


class ProductImage(models.Model):    
    alternative_text = models.CharField(max_length=100)
    url = models.ImageField(upload_to='product_images/')
    productline = models.ForeignKey(ProductLine, on_delete=models.CASCADE, related_name="product_image")
    order = OrderField(unique_for_field="productline", blank=True)

    def clean(self):
        qs = ProductImage.objects.filter(productline=self.productline)
        for obj in qs:
            if self.id != obj.id and self.order == obj.order:
                raise ValidationError("Duplicate value.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(ProductImage, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.order)

class ProductType(models.Model):
    name = models.CharField(max_length=100)
    attribute = models.ManyToManyField(
        Attribute,
        through="ProductTypeAttribute",
        related_name="product_type_attribute",
    )

    def __str__(self):
        return str(self.name)


class ProductTypeAttribute(models.Model):

    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.CASCADE,
        related_name="product_type_attribute_pt",
    )
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        related_name="product_type_attribute_a",
    )

    class Meta:
        unique_together = ("product_type", "attribute")