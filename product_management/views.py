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
    permission_classes = [ProductPermission]  # only editors/managers can upload

    def post(self, request):
        #file = request.FILES['file']
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file uploaded"},status=400)
        df = pd.read_excel(file)
        # Expected columns: Product Name, Product price, discount price, Product fabric type, Colour, sizes, product description
        # Note: 'sizes' might be a comma-separated list? For simplicity, we'll assume each row is a variant.
        # Better to group by product name and colour to create variants.
        # Implementation details...
        for _, row in df.iterrows():
            # Create or get Product
            product, _ = Product.objects.get_or_create(
                name=row['Product Name'],
                defaults={
                    'description': row.get('product description', ''),
                    'fabric_type': row['Product fabric type'],
                    'base_price': row['Product price'],
                    'discount_price': row.get('discount price', None),
                }
            )
            # Create variant for each colour and size
            colours = row['Colour'].split(',')  # if multiple colours in one cell?
            sizes = row['sizes'].split(',')
            for colour in colours:
                for size in sizes:
                    ProductVariant.objects.get_or_create(
                        product=product,
                        colour=colour.strip(),
                        size=size.strip(),
                        price=row['Product price'],
                        discount_price=row.get('discount price', None)
                    )
        return Response({'message': 'Upload successful'})
    