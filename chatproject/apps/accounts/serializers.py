from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )

        return user

class LoginSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=8, max_length=128)
    username = serializers.CharField()

    def validate(self, data):
        user = User.objects.filter(username=data['username']).first()

        if not user or not user.check_password(data['password']):
            raise serializers.ValidationError('Invalid username or password')

        data['user'] = user

        return data

