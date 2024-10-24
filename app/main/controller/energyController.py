from ..service.solarService import SolarService
from ..config.firebaseClient import FireBaseConfig
import requests, os, math
from dotenv import dotenv_values
from fastapi import APIRouter
from ..model.ReponseModel import ReponseModel
from ..model.BuildingDocument import BuildingDocument

energyController = APIRouter()
class EnergyController():
    __solarService = SolarService()
    __firebaseClient = FireBaseConfig()
    __config = dotenv_values(os.getcwd()+"/.env")

    @energyController.get('/sites/list/', response_model=ReponseModel)
    def get_site_by_key()->ReponseModel:
        try:
            site_api_key = EnergyController.\
                __firebaseClient\
                .getFireStoreDB(EnergyController.__config["FIRESTORE_COLLECTION"],\
                                EnergyController.__config["FIRESTORE_SOLAR_DOCUMENT"])\
                                ["solarEdgeKey"]
            res = EnergyController.__solarService.get_site_by_key(site_api_key)
            if not res:
                return ReponseModel(status=200, message="No data")
            return res
        except:
            return ReponseModel(message=str(requests.exceptions.HTTPError),status=500)
        
    @energyController.get('/site/{site_id}/power')
    #all parameter pass as function serve the above annotation are auto grabbed from URL and inject 
    def get_site_power(site_id, startTime, endTime):
        try:
            site_api_key = EnergyController.\
                __firebaseClient\
                .getFireStoreDB(EnergyController.__config["FIRESTORE_COLLECTION"],\
                                EnergyController.__config["FIRESTORE_SOLAR_DOCUMENT"])\
                                ["solarEdgeKey"]
            res = EnergyController.__solarService.get_site_power(site_api_key,startTime,endTime,site_id)
            if not res:
                return ReponseModel(messgae=None, status=200)
            return res
        except:
            return ReponseModel(message=str(requests.exceptions.HTTPError),status=500)
        
    @energyController.get('/site/{site_id}/energy')
    def get_site_energy(site_id, startDate, endDate, timeUnit):
        try:
            site_api_key = EnergyController.\
                __firebaseClient\
                .getFireStoreDB(EnergyController.__config["FIRESTORE_COLLECTION"],\
                                EnergyController.__config["FIRESTORE_SOLAR_DOCUMENT"])\
                                ["solarEdgeKey"]
            res = EnergyController.__solarService.get_site_energy(site_api_key,startDate,endDate,timeUnit,site_id)
            if not res:
                return ReponseModel(message=None, status=200)
            return res
        except:
            return ReponseModel(message=str(requests.exceptions.HTTPError),status=500)

    @energyController.get('/sites')
    def get_sites()->ReponseModel:
        try:
            response=[]
            collection=EnergyController.__firebaseClient.\
                    getFireStoreCollection(EnergyController.__config["FIRESTORE_BUILDING_RESOURCE_COLLECTION"])
            doc_sites = collection.stream()
            for doc in doc_sites:
                doc_data=doc.to_dict()
                if not math.isnan(doc_data["portfolio_manager_id"]): 
                    doc_data["portfolio_manager_id"]=int(doc_data["portfolio_manager_id"])
                else: doc_data["portfolio_manager_id"]=-1
                if not math.isnan(doc_data["solar_edge_id"]):
                    doc_data["solar_edge_id"]=int(doc_data["solar_edge_id"])
                else: doc_data["solar_edge_id"]=-1
                response.append(BuildingDocument(name=doc_data["name"],solarEdge_id=doc_data["solar_edge_id"],portfolio_id=doc_data["portfolio_manager_id"],id=int(doc.id)))
            return ReponseModel(message=response,status=200)
        except:
            return ReponseModel(message=str(requests.exceptions.HTTPError),status=500)