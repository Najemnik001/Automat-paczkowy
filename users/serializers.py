from rest_framework import serializers
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'usersurname', 'email', 'password', 'role']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            usersurname=validated_data['usersurname'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        user.role = validated_data['role']
        user.save()
        return user
