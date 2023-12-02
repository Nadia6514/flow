import openai
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

function_descriptions = [
    {
        "name": "extract_info_from_email",
        "description": "Categorize and extract key information from an email, such as company name, subject, category, next steps, and priority.",
        "parameters": {
            "type": "object",
            "properties": {
                "companyName": {
                    "type": "string",
                    "description": "The name of the company that sent the email"
                },                                        
                "Subject": {
                    "type": "string",
                    "description": "The subject of the email"
                },
                "category": {
                    "type": "string",
                    "description": "Categorize this email into categories like: 1. Press Release 2. Brief; 3. Announcement; 4. Press Conference; 5. Other."
                },
                "nextStep": {
                    "type": "string",
                    "description": "Suggested next step to move this forward"
                },
                "priority": {
                    "type": "string",
                    "description": "Priority score from 0 to 10; 10 being most important"
                },
            },
            "required": ["companyName", "Subject", "category", "nextStep", "priority"]
        }
    }
]

# Example email content (your provided example)
email = """
-----Message d'origine-----
De : Philippe PEJO (Sénat) <p.pejo@senat.fr>
Envoyé : vendredi 1 décembre 2023 17:44
À : isabelle.jouanneau@lafontpresse.fr
Objet : [MASSMAIL] [Sénat] - Réemploi des véhicules : présentation à la presse des conclusions du rapport
...
"""

prompt = f"Please extract key information from this email: {email}"
message = [{"role": "user", "content": prompt}]

response = openai.ChatCompletion.create(
    model="gpt-4-0613",
    messages=message,
    functions=function_descriptions,
    function_call="auto"
)

print(response)

# FastAPI Endpoints
class Email(BaseModel):
    from_email: str
    content: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/")
def analyse_email(email: Email):
    content = email.content
    query = f"Please extract key information from this email: {content}"

    messages = [{"role": "user", "content": query}]

    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=messages,
        functions=function_descriptions,
        function_call="auto"
    )

    arguments = response.choices[0]["message"]["function_call"]["arguments"]
    companyName = eval(arguments).get("companyName")
    priority = eval(arguments).get("priority")
    subject = eval(arguments).get("Subject")
    category = eval(arguments).get("category")
    nextStep = eval(arguments).get("nextStep")

    return {
        "companyName": companyName,
        "subject": subject,
        "category": category,
        "priority": priority,
        "nextStep": nextStep
    }
