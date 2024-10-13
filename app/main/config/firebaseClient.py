from firebase_admin import firestore, credentials, initialize_app
import os
from dotenv import dotenv_values

class FireBaseConfig:
    __config = dotenv_values(os.getcwd()+"/.env")
    def __init__(self):
        self.cred = credentials.Certificate(os.getcwd()+FireBaseConfig.__config["FIREBASE_SDK_DIR"])
        initialize_app(self.cred)
        
    def getFireStoreDB(self, collection, document) -> dict:
        return firestore.client()\
            .collection(collection)\
            .document(document)\
            .get()\
            .to_dict()
