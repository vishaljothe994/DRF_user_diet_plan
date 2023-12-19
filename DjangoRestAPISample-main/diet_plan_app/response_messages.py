
# Messages for user registration
USER_REGISTER_SUCCESS = {
    "message": "User registered successfully",
    "details": "user_details",
}


USER_REGISTER_ERROR = {
    "message": "Failed to register user",
    "details": "errors",
}


# Messages for user login
USER_LOGIN_SUCCESS = {
    "message": "Login successful",
    "details": "user_details",
}


USER_LOGIN_INVALID_CREDENTIALS = {
    "message": "Invalid credentials",
}


# Messages for user profile 
USER_PROFILE_MESSAGES = {
    "missing_user_id": "User Id is missing or invalid",
    "missing_token": "Token is missing or invalid",
    "access_denied": "Access denied",
    "user_not_found": "User not found",
    "message": "success",
}


# Messages for user forgot password
FORGOT_PASSWORD_MESSAGES = {
    "email_sent": "Email has been sent",
    "user_not_found": "User not found",
    "invalid_request": "Invalid request. Please provide a valid email."
}


# Messages for user change password
CHANGE_PASSWORD_MESSAGES = {
    "passwords_not_match": "Passwords do not match",
    "password_updated": "Password updated successfully",
    "user_not_found": "User not found",
    "token_not_found_or_expired": "Token not found or expired",
    "invalid_request": "Invalid request. Please provide necessary data."
}


# Messages for user profile update
USER_PROFILE_UPDATE_MESSAGES = {
    "access_denied": "Access denied",
    "profile_updated": "User profile updated successfully",
    "email_already_exists": "Email already exists",
    "passwords_not_match": "Passwords do not match",
    "invalid_request": "Invalid request. Please provide necessary data."
}


# Messages for create generate plan
CREATE_GENERATE_PLAN_MESSAGES = {
    "success": "Success",
    "try_again_generic": "OOPS! We are encountering some issue, please try again.",
    "trials_left_zero": "You haven't trials left.",
    "user_not_found": "User not found.",
}


# Messages for family member detail
FAMILY_MEMBER_DETAIL_MESSAGES = {
    "user_not_found": "User not found.",
    "internal_error": "An error occurred.",
    "error": "Family information not found for the provided user ID."
}
