from ..service.solarService import SolarService
from ..config.firebaseClient import FireBaseConfig
import requests, os
from dotenv import dotenv_values
from fastapi import APIRouter
from ..model.ReponseModel import ReponseModel

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

    
    @energyController.get('/site/{id}/quick_insights/')
    def get_quick_insights(id: int, quickInsightsType: str) -> ReponseModel:
        try:
            site_api_key = EnergyController.__firebaseClient.getFireStoreDB(
                EnergyController.__config["FIRESTORE_COLLECTION"],
                EnergyController.__config["FIRESTORE_SOLAR_DOCUMENT"]
            )["solarEdgeKey"]
            
            # Retrieve insights based on the quickInsightsType
            if quickInsightsType == "solar":
                res = EnergyController.__solarService.get_solar_insights(site_api_key, id)
            elif quickInsightsType == "electric":
                res = EnergyController.__portfolioService.get_electric_insights(site_api_key, id)
            elif quickInsightsType == "natural_gas":
                res = EnergyController.__portfolioService.get_gas_insights(site_api_key, id)
            else:
                return ReponseModel(message="Invalid insights type", status=400)
            
            # Check if response is empty
            if not res:
                return ReponseModel(message="No data available", status=200)
            
            # Transform the data into the required format
            # insights_data = {
            #     "id": id,
            #     "installedOn": res.get("installedOn"),
            #     "lifetimeEnergy": res.get("lifetimeEnergy"),
            #     "recentMonthEnergy": res.get("recentMonthEnergy"),
            #     "energyUnit": res.get("energyUnit")
            # }

            return ReponseModel(message=res, status=200)
        except Exception as e:
            return ReponseModel(message=str(e), status=500)


    