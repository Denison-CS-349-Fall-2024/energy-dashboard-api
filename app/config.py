import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    API_KEY_SOLAR_EDGE = os.getenv("API_KEY_SOLAR_EDGE")
    USERNAME_ENERGY_STAR = os.getenv("USERNAME_ENERGY_STAR")
    PASSWORD_ENERGY_STAR = os.getenv("PASSWORD_ENERGY_STAR")
    FIREBASE_CREDENTIALS_JSON = {
        "type": os.getenv("FIREBASE_TYPE"),
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY"),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
        "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
        "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv(
            "FIREBASE_AUTH_PROVIDER_X509_CERT_URL"
        ),
        "client_x509_cert_url": os.getenv("FIREBASE_X509_CERT_URL"),
        "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN"),
    }
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


settings = Settings()
