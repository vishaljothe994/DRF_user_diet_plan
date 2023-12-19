from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.tokens import AccessToken
from .utils import decrypt
from .models import FamilyInfo, MemberDetail


class UserSerializer(serializers.ModelSerializer):
    # Serializer for the User model

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'isPaid', 'TrialsLeft', 'createdAt', 'updatedAt']

    def create(self, validated_data):
        # Create a new user instance with validated data
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    # Serializer for user details

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'isPaid', 'TrialsLeft', 'createdAt', 'updatedAt']


class EmailSerializer(serializers.Serializer):
    # Serializer for email input for forgot password sendmail function

    email = serializers.EmailField()


class ChangePasswordRequestSerializer(serializers.Serializer):
    # Serializer for changing user password

    token = serializers.CharField()
    newPassword = serializers.CharField()
    confirmPassword = serializers.CharField()


class UserProfileUpdateSerializer(serializers.Serializer):
    # Serializer for updating user profile

    full_name = serializers.CharField(max_length=255, required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(max_length=255, required=False)
    confirm_password = serializers.CharField(max_length=255, required=False)


class MemberDetailSerializer(serializers.ModelSerializer):
    # Serializer for MemberDetail model

    class Meta:
        model = MemberDetail
        fields = '__all__'

class FamilyInfoSerializer(serializers.ModelSerializer):
    # Serializer for FamilyInfo model
    
    members = MemberDetailSerializer(many=True, read_only=True)
    class Meta:
        model = FamilyInfo
        fields = '__all__'


class GetFamilyInfoSerializer(serializers.ModelSerializer):
     # Serializer for Get FamilyInfo and Member info in decrypted form
    members = MemberDetailSerializer(source='memberdetail_set', many=True, read_only=True)

    class Meta:
        model = FamilyInfo
        fields = ['userId', 'noOfMembers', 'national', 'diet', 'ethnicity', 'createdAt', 'updatedAt', 'meal', 'members']



  







