from firebase_admin import firestore, credentials, initialize_app
import os
from dotenv import dotenv_values

class FireBaseConfig:
    __client = None
    __config = dotenv_values(os.getcwd()+"/.env")

    def __init__(self):
        self.cred = credentials.Certificate(os.getcwd()+FireBaseConfig.__config["FIREBASE_SDK_DIR"])
        self.load_client()
    def load_client(self):
        if FireBaseConfig.__client != None: 
            return FireBaseConfig.__client
        else:
            FireBaseConfig.__client = initialize_app(self.cred)
            if not FireBaseConfig.__client: raise Exception("Cannot initialize Firebase Client")
            return FireBaseConfig.__client

        
    def getFireStoreDB(self, collection, document) -> dict:
        return firestore.client()\
            .collection(collection)\
            .document(document)\
            .get()\
            .to_dict()
    
    def getFireStoreCollection(self,collection):
        return firestore.client().collection(collection) 
