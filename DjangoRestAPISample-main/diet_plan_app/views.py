from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    EmailSerializer,
    ChangePasswordRequestSerializer,
    UserProfileUpdateSerializer,
    FamilyInfoSerializer,
    MemberDetailSerializer,
    GetFamilyInfoSerializer
)
from .models import User, UserToken
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
import random
import string
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework_simplejwt.tokens import AccessToken
from .models import FamilyInfo, MemberDetail
import jsonschema
import json
from .utils import chat_with_gpt, generate_dynamic_schema, encrypt, decrypt, generate_prompt, generate_short_token
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.db import transaction
from .email_utils import generate_reset_password_email, send_email_to_admin
from .response_messages import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class UserRegistrationView(APIView):

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name', 'email', 'password'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        operation_description='Handles user registration with name, email and password.'
    )

    def post(self, request):
        """
        Handle user registration.
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            response_data = {
                # "message": "User registered successfully",
                **USER_REGISTER_SUCCESS,
                "user": {
                    "fullName": user.name,
                    "email": user.email,
                    "password": user.password,
                    "isPaid": user.isPaid,
                    "TrialsLeft": user.TrialsLeft,
                    "createdAt": user.createdAt,
                    "updatedAt": user.updatedAt,
                },
                "id": str(user.id),
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response({USER_REGISTER_ERROR["message"]: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        operation_description='Handles user login with email and password.'
    )

    def post(self, request):
        """
        Handle user login.
        """
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)

            refresh_token = refresh
            access_token = refresh.access_token

            serializer = UserProfileSerializer(user)

            response_data = {
                **USER_LOGIN_SUCCESS,
                "user": serializer.data,
                "access_token": str(access_token),
            }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response({'error': USER_LOGIN_INVALID_CREDENTIALS}, status=status.HTTP_401_UNAUTHORIZED)


class getUserProfilebyId(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        """
        Get user profile.
        """
        user = request.user
        if user:
            user_id_from_token = user.id
            # user_id_from_request = request.data.get('user_id')

            if user_id is None:
                return Response({"error": USER_PROFILE_MESSAGES["missing_user_id"]}, status=status.HTTP_401_UNAUTHORIZED)

            if user_id_from_token is None:
                return Response({"error": USER_PROFILE_MESSAGES["missing_token"]}, status=status.HTTP_401_UNAUTHORIZED)

            if user_id_from_token != user_id:
                return Response({"error": USER_PROFILE_MESSAGES["access_denied"]}, status=status.HTTP_403_FORBIDDEN)

            serializer = UserProfileSerializer(user)
            return Response(serializer.data or {"message": USER_PROFILE_MESSAGES["message"]}, status=status.HTTP_200_OK)
        else:
            return Response({"error": USER_PROFILE_MESSAGES["user_not_found"]}, status=status.HTTP_404_NOT_FOUND)


class forgot_password_email(APIView):

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        operation_description='Handles forgot password email request.'
    )

    def post(self, request):
        """
        Handle forgot password email request.
        """
        email_serializer = EmailSerializer(data=request.data)
        if email_serializer.is_valid():
            email_data = email_serializer.validated_data
            user = User.objects.filter(email=email_data['email']).first()

            if user:
                token = generate_short_token(length = 20)
                UserToken.objects.update_or_create(user=user, defaults={'token': token})
                send_mail = generate_reset_password_email(user, token, email_data)

                return Response({"message": FORGOT_PASSWORD_MESSAGES["email_sent"]}, status=status.HTTP_200_OK)
            else:
                return Response({"error": FORGOT_PASSWORD_MESSAGES["user_not_found"]}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(email_serializer.errorsor or {"error": FORGOT_PASSWORD_MESSAGES["invalid_request"]}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordReset(APIView):

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING),
                'newPassword': openapi.Schema(type=openapi.TYPE_STRING),
                'confirmPassword': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        operation_description='Handle change password request.'
    )

    def post(self, request):
        """
        Handle change password request.
        """
        serializer = ChangePasswordRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            token = request.data.get("token")
            new_password = request.data.get("newPassword")
            confirm_password = request.data.get("confirmPassword")

            if new_password != confirm_password:
                return Response({"error": CHANGE_PASSWORD_MESSAGES["passwords_not_match"]}, status=status.HTTP_400_BAD_REQUEST)

            user_token = UserToken.objects.filter(token=token).first()

            if user_token:
                user = User.objects.filter(email=user_token.user).first()

                if user:
                    user.set_password(new_password)
                    user.save()
                    return Response({"message": CHANGE_PASSWORD_MESSAGES["password_updated"]}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": CHANGE_PASSWORD_MESSAGES["user_not_found"]}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": CHANGE_PASSWORD_MESSAGES["token_not_found_or_expired"]}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errorsor or {"error": CHANGE_PASSWORD_MESSAGES["invalid_request"]}, status=status.HTTP_400_BAD_REQUEST)
 

class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'full_name': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                'confirm_password': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        operation_description='Handles user profile update with user data.',
    )
    
    def put(self, request, user_id):
        """
        Handle user profile update.
        """
        user = request.user
        print("user", user)
        print("user", user.id)


        # Check if the user has permission to update the profile
        if user.id != int(user_id):
            return Response({"error": USER_PROFILE_UPDATE_MESSAGES["access_denied"]}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserProfileUpdateSerializer(data=request.data)
        if serializer.is_valid():
            # user = request.user
            data = serializer.validated_data

            if data.get('full_name'):
                user.name = data['full_name']

            if data.get('email'):
                new_email = data['email']
                if User.objects.filter(email=new_email).exclude(id=user.id).exists():
                    return Response({'email': USER_PROFILE_UPDATE_MESSAGES["email_already_exists"]}, status=status.HTTP_400_BAD_REQUEST)
                user.email = new_email

            if data.get('password'):
                password = data['password']
                confirm_password = data.get('confirm_password')

                if password != confirm_password:
                    return Response({'password': USER_PROFILE_UPDATE_MESSAGES["passwords_not_match"]}, status=status.HTTP_400_BAD_REQUEST)

                user.set_password(password)

            user.save()

            response_data = {
                "message": USER_PROFILE_UPDATE_MESSAGES["profile_updated"],
                "user": {
                    "full_name": user.name,
                    "email": user.email,
                }
            }

            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors or {"detail": USER_PROFILE_UPDATE_MESSAGES["invalid_request"]}, status=status.HTTP_400_BAD_REQUEST)


class CreateGeneratePlan(APIView):
    """
    Handle Create Generate plans for User as per the trial left.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'userId': openapi.Schema(type=openapi.TYPE_INTEGER),
            'noOfMembers': openapi.Schema(type=openapi.TYPE_INTEGER),
            'national': openapi.Schema(type=openapi.TYPE_STRING),
            'meal': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
            'diet': openapi.Schema(type=openapi.TYPE_STRING),
            'ethnicity': openapi.Schema(type=openapi.TYPE_STRING),
            'members': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'userId': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                        'allergy': openapi.Schema(type=openapi.TYPE_STRING),
                        'medicalCondition': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
        },
        required=['userId', 'noOfMembers', 'national', 'meal', 'diet', 'ethnicity', 'members'],
    ),
    operation_description='Handles user data input with user and member information.'
    )

    def post(self, request, format=None):
            # Extract family info data from the request
            family_info_data = request.data
            try:
                # Get user data based on the 'userId' from the family info data
                user_data = User.objects.get(id=family_info_data['userId'])
                trials_left = user_data.TrialsLeft

                if trials_left > 0:
                    # Retrieve family data information
                    family_data_information = self.getFamilyData(family_info_data)
                    print("family_data_information====>>>>" , family_data_information)

                    response_list = []
                    num_response = 2

                    for i in range(num_response):
                        # Call the chat_with_gpt function with family data and get a response
                        response = chat_with_gpt(family_data_information)
                        print("response ====    >>>>, " , i,  response)
 
                        try:
                            # Try to parse the response as JSON
                            resp_data = json.loads(response)
                            if isinstance(resp_data, list):
                                response_list.append(response)
                                break

                        except json.JSONDecodeError:
                            if i == 1:
                                # To send an email to admin
                                send_email_to_admin(response)
                                return Response({"message": CREATE_GENERATE_PLAN_MESSAGES["try_again_generic"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                    if response_list:
                        for response_json in response_list:
                            try:
                                response2 = [json.loads(response_json) for response_json in response_list]

                                if isinstance(response2, list):
                                    # Decrease the user's trials left count and save the user data
                                    user_data = User.objects.get(id=family_info_data['userId'])
                                    user_data.TrialsLeft -= 1
                                    user_data.save()
                                    user_serializer = UserSerializer(user_data)

                                    return Response({
                                        "message": CREATE_GENERATE_PLAN_MESSAGES["success"],
                                        "data": response_json,
                                        "updateData": user_serializer.data
                                    }, status=status.HTTP_200_OK)

                            except json.JSONDecodeError:
                                # To send an email to admin
                                send_email_to_admin(response_json)
                                return Response({"message": CREATE_GENERATE_PLAN_MESSAGES["try_again_generic"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                                    

                        return Response({"message": CREATE_GENERATE_PLAN_MESSAGES["try_again_generic"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    else:
                        # To send an email to admin
                        send_email_to_admin(response)
                        return Response({"message": CREATE_GENERATE_PLAN_MESSAGES["try_again_generic"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return Response({"message": CREATE_GENERATE_PLAN_MESSAGES["trials_left_zero"]})
            except ObjectDoesNotExist:
                # Return a response if the user is not found
                return Response({"message": CREATE_GENERATE_PLAN_MESSAGES["user_not_found"]}, status=status.HTTP_404_NOT_FOUND)



    def getFamilyData(self, family_info_data):
        try:
            members_data = family_info_data.pop("members")

            user_id = family_info_data.get("userId")
            family_info = FamilyInfo.objects.get(userId=user_id)

            family_info_serializer = FamilyInfoSerializer(instance=family_info, data=family_info_data)
        except ObjectDoesNotExist:
            family_info_serializer = FamilyInfoSerializer(data=family_info_data)
            if family_info_serializer.is_valid():
                family_info = family_info_serializer.save()
            else:
                return "Invalid Family Information"

        family_meal_str = ', '.join(family_info.meal)
        dynamic_schema = generate_dynamic_schema(family_info.meal)
        dynamic_schema_json = json.dumps(dynamic_schema)

        member_detail = []

        for member_data in members_data:
            family_info_id = family_info.id if family_info else None
            member_data["familyInfoId"] = family_info_id

            allergy1 = member_data["allergy"]
            medical_condition1 = member_data["medicalCondition"]

            allergy = encrypt(allergy1) if allergy1 else None
            medical_condition = encrypt(medical_condition1) if medical_condition1 else None

            allergy = allergy.decode() if allergy else None
            medical_condition = medical_condition.decode() if medical_condition else None

            member_data["allergy"] = allergy
            member_data["medicalCondition"] = medical_condition
            member_data["familyInfoId"] = family_info.id

            member_serializer = MemberDetailSerializer(data=member_data)
            member_detail.append(f'1 person is allergic to {allergy1} and has a medical history of {medical_condition1}.')

            if member_serializer.is_valid():
                member_serializer.save()
            else:
                print("Validation errors:", member_serializer.errors)
                print("data not saved")

        prompt = generate_prompt(family_info, dynamic_schema_json, family_meal_str, member_detail)
        return prompt

            
class FamilyMemberDetailByUserId(APIView):    
    """
    Handle Get Family and member data .
    """
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id):
        try:
            family_info = FamilyInfo.objects.get(userId=user_id)
            serializer = GetFamilyInfoSerializer(family_info)

            # Decrypt allergy and medicalCondition for each member
            for member in serializer.data['members']:
                member['allergy'] = decrypt(member['allergy'])
                member['medicalCondition'] = decrypt(member['medicalCondition'])

            return Response(serializer.data)
        except FamilyInfo.DoesNotExist:
            return Response({"message": FAMILY_MEMBER_DETAIL_MESSAGES["user_not_found"]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
           
















