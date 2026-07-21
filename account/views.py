from django.shortcuts import render, redirect
from django.db import models
from django.http import HttpResponse
from django.contrib.auth import get_user_model

User = get_user_model()

def signup(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")

        User.objects.create_user(
            username=email,      # Using email as username
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            role=role,
        )

        return HttpResponse("User Created Successfully")

    return render(request, "signup.html")


# views.py

from django.contrib.auth import authenticate, get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny

User = get_user_model()


class LoginAPIView(APIView):
    authentication_classes = []

    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Static OTP (assignment requirement)
        request.session["otp_user_id"] = user.id
        request.session["otp_code"] = "123456"

        return Response(
            {
                "message": "OTP sent successfully.",
            },
            status=status.HTTP_200_OK,
        )


class VerifyOTPAPIView(APIView):
    permission_classes = []
    authentication_classes = []


    def post(self, request):
        otp = request.data.get("otp")

        if not otp:
            return Response(
                {"error": "OTP is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_id = request.session.get("otp_user_id")
        stored_otp = request.session.get("otp_code")

        if user_id is None:
            return Response(
                {"error": "Login first."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if otp != stored_otp:
            return Response(
                {"error": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        refresh = RefreshToken.for_user(user)

        # Clear OTP session
        request.session.pop("otp_user_id", None)
        request.session.pop("otp_code", None)


        response = Response({
            "message": "Login Successful"
        })

        response.set_cookie(
            key="access_token",
            value=str(refresh.access_token),
            httponly=True,
            secure=False,      # True in production (HTTPS)
            samesite="Lax",
        )

        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite="Lax",
        )

        return response

