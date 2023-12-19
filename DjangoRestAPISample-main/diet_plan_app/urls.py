from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    getUserProfilebyId,
    forgot_password_email,
    ChangePasswordReset,
    UserProfileUpdateView,
    CreateGeneratePlan,
    FamilyMemberDetailByUserId, 
)


urlpatterns = [
    # Endpoint for user registration
    path('createUser', UserRegistrationView.as_view(), name='user_registration'),

    # Endpoint for user login
    path('login', UserLoginView.as_view(), name='user_login'),

    # Endpoint for fetching user details
    path('getUserProfile/<int:user_id>/', getUserProfilebyId.as_view(), name='getUserProfile'),

    # Endpoint for updating user details
    path('updateUserDetail/<int:user_id>', UserProfileUpdateView.as_view(), name='update_user_detail'),

    # Endpoint for sending forgot password email
    path('forgot_password', forgot_password_email.as_view(), name='forgot_password_email'),

    # Endpoint for changing user password
    path('change_password', ChangePasswordReset.as_view(), name='change_password_reset'),

    # Endpoint for create generate plan
    path('createGeneratePlan', CreateGeneratePlan.as_view(), name='create-generate-plan'),

    # Endpoint for getFamliyMemberInfo
    path('getFamliyMemberInfo/<int:user_id>/', FamilyMemberDetailByUserId.as_view(), name='family-member-detail-by-user'),

]






