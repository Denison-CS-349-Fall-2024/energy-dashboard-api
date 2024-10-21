from ..service.solarService import SolarService
from ..config.firebaseClient import FireBaseConfig
import requests, os, uuid
from dotenv import dotenv_values
from fastapi import APIRouter
from ..model.ReponseModel import ReponseModel
from ..model.BuildingDocument import BuildingDocument

firebaseController = APIRouter()
class FireStoreController():
    __firebaseClient = FireBaseConfig()
    __config = dotenv_values(os.getcwd()+"/.env")

    @firebaseController.post('/firestore/write-building-resource', response_model=ReponseModel)
    def addBuilding(building:BuildingDocument)->ReponseModel:
        if FireStoreController.__firebaseClient:
            try:
                collection=FireStoreController.__firebaseClient.\
                    getFireStoreCollection(FireStoreController.__config["FIRESTORE_BUILDING_RESOURCE_COLLECTION"])
                collection.add(building.to_dict(),str(uuid.uuid4()))
                return ReponseModel(message=building.__repr__(), status=200)
            except:
                return ReponseModel(message=str(requests.exceptions.RequestException),status=500)
            
        else: 
            return ReponseModel(message="Cannot update Firestore Collection fireBaseClient not initialized", status=500)