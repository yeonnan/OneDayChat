from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        user = User.objects.create_user(
            username = validated_data['username'],
            password = validated_data['password'],
            email = validated_data['email'],
            nickname = validated_data['nickname']
        )
        return user
    

class ChangePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        models = User
        fields = ['password']

    
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('비밀번호는 8글자 이상이어야 합니다.')
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError('비밀번호에 숫자가 포함되어야 합니다.')
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError('비밀번호에 대문자가 포함되어야 합니다.')
        if not any(char in "!@#$%^&*()_+" for char in value):
            raise serializers.ValidationError('비밀번호에 특수문자가 포함되어야 합니다.')
        return value
    
    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance