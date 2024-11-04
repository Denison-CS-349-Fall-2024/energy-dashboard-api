from dotenv import load_dotenv
from firebase_admin import credentials, firestore_async, initialize_app

from app.config import settings

load_dotenv()

cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_JSON)
initialize_app(cred)

db = firestore_async.client()
