from rest_framework import serializers
from .models import Product, ProductVariant


class ProductVariantSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductVariant
        fields = [
            "colour",
            "size",
            "price",
            "discount_price",
            "stock",
        ]


class ProductSerializer(serializers.ModelSerializer):

    variants = ProductVariantSerializer(many=True,required=False)

    class Meta:
        model = Product
        fields = "__all__"


    def create(self, validated_data):

        # get variants data
        variants_data = validated_data.pop("variants", [])

        # create product
        product = Product.objects.create(**validated_data)

        # create variants
        for variant_data in variants_data:
            ProductVariant.objects.create(
                product=product,
                **variant_data
            )

        return product