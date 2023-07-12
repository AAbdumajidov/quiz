from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .permissions import IsOwnerOrReadOnly
from .models import Account
from .serializers import RegisterSerializer, LoginSerializer, MyProfileSerializer


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'data': "Account successfully created"}, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'tokens': serializer.data}, status=status.HTTP_200_OK)


class MyProfileRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = MyProfileSerializer
    permission_classes = [IsOwnerOrReadOnly]