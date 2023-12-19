
## Project Overview:
The project is a Django REST Framework (DRF) application designed for managing user profiles, family details, and creating meal plans. 
It focuses on ensuring data privacy by storing all member details in encrypted form. 

## Getting Started

These instructions will help you set up and run the project on your local machine.

### Prerequisites

List any prerequisites required to run the project, such as Python and Django versions, dependencies, or other software.

### Installation

A step-by-step guide to installing your project.

1. Create a virtual environment:
python -m venv venv

2. Activate the virtual environment:
On Windows:
venv\Scripts\activate

OnLinux:
source venv/bin/activate

3. Install project dependencies:
pip install -r requirements.txt


4. Update Cipher suit Key for Encrypt and Decrypt User data in settings
CIPHER_SUITE_KEY = "*****KEY******"  # Replace with your CIPHER_SUITE_KEY

5. Update Email configuration in settings
   
6. Install & Update MySQL Database configration in settings and add credentials and create a database on mysql and mention the name on setting.py.

7. Apply database migrations:
python manage.py makemigrations
python manage.py migrate

8. Update configration of Django Rest Framework SimpleJWT in settings

9. Add Open API Key in setting
    OPEN_API_KEY = "*****KEY******"   # Replace with your OPEN_API_KEY

10. Start the development server:
python manage.py runserver


11. **Swagger API Documentation**
    The Swagger UI provides an interactive documentation interface for the API endpoints in this project.
    To access the Swagger documentation, follow these steps:
    
    1. Make sure the RestAPI application is running.
    2. Open a web browser.
    3. Enter the following URL in the address bar: http://127.0.0.1:8000/swagger/
    4. You'll be redirected to the Swagger UI, displaying the API endpoints, their descriptions, and methods.
    5. Create new user with create_user API and login with Login API using crendentials and when you login you get a JWT token,
       Put JWT token like "Bearer *****JWT_TOKEN*****" in Authorize and after you can have access permissions. 

12. Review the Postman DOc for API documentation provided, such as Postman collections or API endpoint details, to understand how to interact with the application.









