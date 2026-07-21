from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer
from .permissions import ProductPermission
from rest_framework import status


from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
import pandas as pd
from .models import Product, ProductVariant


from rest_framework.permissions import BasePermission


class PublishPermission(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "type1"
        )



class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [ProductPermission]


    @action(detail=True, methods=["patch"])
    def publish(self, request, pk=None):

        product = self.get_object()

        product.is_published = True
        product.save()

        return Response({
            "message": "Product published successfully"
        })


    @action(detail=True, methods=["patch"])
    def unpublish(self, request, pk=None):

        product = self.get_object()

        product.is_published = False
        product.save()

        return Response({
            "message": "Product unpublished successfully"
        })


class BulkUploadView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [ProductPermission]

    def post(self, request):

        file = request.FILES.get("file")

        if not file:
            return Response(
                {"error": "No file uploaded"},
                status=400
            )

        df = pd.read_excel(file)

        products_to_create = []
        variants_to_create = []

        # Get existing products
        product_names = df['Product Name'].unique()

        existing_products = {
            product.name: product
            for product in Product.objects.filter(
                name__in=product_names
            )
        }
        print(existing_products)

        # -----------------------------
        # Create Products
        # -----------------------------
        for _, row in df.iterrows():
            print(row)

            product_name = row['Product Name']

            if product_name not in existing_products:

                product = Product(
                    name=product_name,
                    description=row.get(
                        'product description',
                        ''
                    ),
                    fabric_type=row['Product fabric type'],
                    base_price=row['Product price'],
                    discount_price=row.get(
                        'discount price',
                        None
                    ),
                    is_published=True
                )

                products_to_create.append(product)


        # Bulk create products
        if products_to_create:

            Product.objects.bulk_create(
                products_to_create
            )

            # Get newly created products with IDs
            new_products = Product.objects.filter(
                name__in=[
                    p.name for p in products_to_create
                ]
            )

            for product in new_products:
                existing_products[product.name] = product #updating existing product



        # -----------------------------
        # Create Variants (Optional)
        # -----------------------------
        existing_variants = set(
            ProductVariant.objects.values_list(
                'product_id',
                'colour',
                'size'
            )
        )


        for _, row in df.iterrows():

            product = existing_products[
                row['Product Name']
            ]

            colour_value = row.get('Colour')
            size_value = row.get('sizes')


            # Skip variant creation
            # if colour or size is missing
            if pd.isna(colour_value) or pd.isna(size_value):
                continue


            colours = str(colour_value).split(',')
            sizes = str(size_value).split(',')


            for colour in colours:

                for size in sizes:

                    colour = colour.strip()
                    size = size.strip()


                    variant_key = (
                        product.id,
                        colour,
                        size
                    )


                    if variant_key not in existing_variants:

                        variants_to_create.append(
                            ProductVariant(
                                product=product,
                                colour=colour,
                                size=size,
                                price=row['Product price'],
                                discount_price=row.get(
                                    'discount price',
                                    None
                                )
                            )
                        )


        # Bulk create variants
        if variants_to_create:

            ProductVariant.objects.bulk_create(
                variants_to_create,
                batch_size=1000
            )


        return Response(
            {
                "message": "Upload successful",
                "products_created": len(products_to_create),
                "variants_created": len(variants_to_create)
            }
        )