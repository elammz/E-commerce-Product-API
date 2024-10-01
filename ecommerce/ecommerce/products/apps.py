from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ecommerce.products"  #django will not find the app with out ecommerce. since we created it inside the projects folder
