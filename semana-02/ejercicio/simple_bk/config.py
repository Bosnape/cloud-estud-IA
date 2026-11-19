import os
from dotenv import load_dotenv

load_dotenv()

CRIPTO_SECRET_KEY = str(os.getenv("SECRET_KEY"))
APP_ENV = os.getenv("APP_ENV", "development")
PORT = os.getenv("PORT", "8000")


if not CRIPTO_SECRET_KEY:
    raise ValueError("CRIPTO_SECRET_KEY is missing from environment variables \n Hey, la variable SECRET_KEY no está definida en el archivo .env \n Por favor, define la variable SECRET_KEY en el archivo .env")
