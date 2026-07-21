from django.db import models

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    fabric_type = models.CharField(max_length=100)
    # Common price/discount (can be overridden per variant)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    SIZE_CHOICES = (
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
    )
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    colour = models.CharField(max_length=50)
    size = models.CharField(max_length=2, choices=SIZE_CHOICES)
    # Optional override per variant
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)  # if inventory needed

    class Meta:
        unique_together = ('product', 'colour', 'size')  # avoid duplicates
        