from django.conf import settings
import openai
import string
import random
from cryptography.fernet import Fernet
import string
import random


## Generate encryption key
cipher_suite_key = settings.CIPHER_SUITE_KEY
cipher_suite = Fernet(cipher_suite_key)


# Custom encryption function
def encrypt(plaintext):
    return cipher_suite.encrypt(plaintext.encode())


# Custom decryption function
def decrypt(ciphertext):
    return cipher_suite.decrypt(ciphertext).decode()

def generate_short_token(length):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))


# Set the API key for the OpenAI service
openai.api_key = settings.OPEN_API_KEY

def chat_with_gpt(prompt):
    # Generate a response using the OpenAI service  
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=3500,  # Adjust as needed
        temperature=0.6,  # Adjust as needed
        n=1,
        stop=None,
    )

    if response.choices: 
        return response.choices[0].text.strip()
    else:
        return ""


def generate_dynamic_schema(field_names):
    # Initialize the schema as an array of objects
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {}
        }
    }
    
    # Get a reference to the 'properties' and 'required' fields within the schema
    properties = schema["items"]["properties"]
    required = ["weekDay"]   # By default, include 'weekDay' as a required field
    
    for field_name in field_names:
        properties[field_name] = {"type": "string"}
        required.append(field_name)
    
    schema["items"]["required"] = required

    return schema


# Create a prompt for generating a meal plan
def generate_prompt(family_info, dynamic_schema_json, family_meal_str, member_detail):   
            # Create a prompt for generating a meal plan
            prompt = f'''Create a Unique 7-day {family_info.diet} {family_info.ethnicity} {family_meal_str} meal plan for
                        {family_info.noOfMembers} family members, considering the availability of ingredients
                        in {family_info.national}. While ensuring that there is at least two varieties of meals
                        for the family members and that there are no non-vegetarian components in the
                        vegetarian meal plan and no vegetarian meals in the non-vegetarian meal plan.
                    '''

            # Add information about family members' allergies and medical conditions to the prompt
            prompt += '\n'.join(member_detail)

            prompt = prompt + f'''\nIt can be arranged in JSON schema format type
                            \n\n{dynamic_schema_json}\n\n. Please provide the meal plan in JSON format.'''              

            return prompt        