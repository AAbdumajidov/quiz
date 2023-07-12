from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'username', 'first_name', 'last_name', 'image', 'bio']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=218)
    password2 = serializers.CharField(max_length=218)

    class Meta:
        model = Account
        fields = ['username', 'password', 'password2', 'first_name', 'last_name', 'image', 'bio', 'created_date']

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')

        if password != password2:
            raise serializers.ValidationError("Password does not match! Try again.")
        return attrs

    def create(self, validated_data):
        del validated_data['password2']
        return Account.objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=218, required=True)
    password = serializers.CharField(max_length=218, write_only=True)
    tokens = serializers.SerializerMethodField(read_only=True)

    def get_tokens(self, obj):
        username = obj.get('username')
        tokens = Account.objects.get(username=username).tokens
        return tokens

    class Meta:
        model = Account
        fields = ['username', 'password', 'tokens']

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise AuthenticationFailed({'message': "Username or Password wrong, Please try again!"})
        if not user.is_active:
            raise AuthenticationFailed({'message': "Account Disabled"})
        return attrs


class MyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['username', 'first_name', 'last_name', 'bio', 'created_date']
