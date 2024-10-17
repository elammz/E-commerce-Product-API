from django.db.models.signals import post_save
from django.contrib.auth.models import User, Permission
from django.dispatch import receiver

@receiver(post_save, sender=User)
def assign_default_permissions(sender, instance, created, **kwargs):
    if created:
        instance.is_staff = True
        instance.save()
        # List of product-related permissions to assign to each registered user
        permissions = [
            Permission.objects.get(codename='add_product'),
            Permission.objects.get(codename='change_product'),
            Permission.objects.get(codename='delete_product'),
            Permission.objects.get(codename='view_product'),
            Permission.objects.get(codename='add_productline'),
            Permission.objects.get(codename='change_productline'),
            Permission.objects.get(codename='delete_productline'),
            Permission.objects.get(codename='view_productline'),
            Permission.objects.get(codename='view_productlineattributevalue'),
            Permission.objects.get(codename='view_producttype'),
            Permission.objects.get(codename='view_producttypeattribute'),
            Permission.objects.get(codename='view_logentry'),
            Permission.objects.get(codename='view_attribute'),
            Permission.objects.get(codename='view_attributevalue'),
            Permission.objects.get(codename='view_brand'),
            Permission.objects.get(codename='view_category'),
            Permission.objects.get(codename='add_productimage'),
            Permission.objects.get(codename='change_productimage'),
            Permission.objects.get(codename='delete_productimage'),
            Permission.objects.get(codename='view_productimage'),
            Permission.objects.get(codename='view_session'),
        ]
        
        # Assign each permission to the newly registered user
        for permission in permissions:
            instance.user_permissions.add(permission)
