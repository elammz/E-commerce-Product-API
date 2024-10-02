from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

class Category(MPTTModel):
    name = models.CharField(max_length=100, unique=True)
    parent = TreeForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)

    class MPTTMeta:
        order_insertion_by = ["name"]

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description =models.TextField(blank=True)
    is_digital = models.BooleanField(default=False) # Defines if the product is shippable or to download
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE) #If the Brand is deleted we won't have Product (it all will be deleted)
    category = TreeForeignKey(
        "Category", on_delete=models.SET_NULL, null=True, blank=True
    ) # null and blank defines that some products may not be part of the category


    def __str__(self):
        return self.name