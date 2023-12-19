
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


def generate_reset_password_email(user, token, email_data):
    reset_link = f"tummytngo.com/reset-password?token={token}"

    html_message = f"""
    <p style="margin-bottom: 20px;">
        Dear <strong>{user.name.title()}</strong>,
    </p>

    <p style="margin-bottom: 20px;">
        A request has been received to reset your password on Tummy Tango. If you did not make any change-password request, please ignore this mail, and make sure 
        you secure your account by changing your password any time soon.
    </p>

    <p style="margin-bottom: 20px;">
        To reset your Password, please click on the link below... 
    </p>
    <a href="{reset_link}">{reset_link}</a>

    <p style="margin-bottom: 20px;">
        Best Wishes,
        <br>
        Tummy Tango
    </p>
    """
    send_mail(
        'Forgot Password Request',  # Subject
        '', 
        settings.SENDER_EMAIL, # Sender email
        [email_data['email']],  # Recipient list
        html_message=html_message,  # HTML message
        fail_silently=False,
    )


@csrf_exempt
def send_email_to_admin(request):
    try:
        # Create the email content with an HTML template
        subject = "Invalid Meal Plan Response"
        reciever_admin_email = settings.RECIEVER_EMAIL
        sender_email = settings.SENDER_EMAIL
        html_template = f"Invalid Meal Plan Response.\n\n {request}"

        send_mail(
            subject,
            html_template,
            sender_email,
            reciever_admin_email,
            fail_silently=False,
        )
        print("Email sent to admin successfully")

    except Exception as e:
        print(f"Error sending email to admin: {str(e)}")