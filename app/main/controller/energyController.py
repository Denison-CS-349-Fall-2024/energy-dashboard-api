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

            # call function the get cookie automatically instead of hardcode
            cookie_string = "JSESSIONID=5B4D0396A34CCDCFA497170B072B1D2C; _gid=GA1.2.614391232.1729565242; cebs=1; org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=en; _ce.clock_data=11%2C140.141.4.65%2C1%2C09993ab868f470cf24e26fa4f9439d9e%2CChrome%2CUS; _gat_EPA=1; cebsp_=13; _ce.s=v~47a73f1dab4c828e0dd85e60bb5608c1834fbe87~lcw~1729718368932~vir~new~lva~1729565247386~vpv~0~v11.fhb~1729565248010~v11.lhb~1729718353983~v11.cs~170423~v11.s~74046390-9184-11ef-a886-ab8aa5eafe49~v11.sla~1729718369973~v11.send~1729718368541~lcw~1729718369973; _ga_2SEC4V3SK9=GS1.1.1729716557.6.1.1729718370.0.0.0; _ga_S0KJTVVLQ6=GS1.1.1729716557.6.1.1729718370.0.0.0; _ga_CSLL4ZEK4L=GS1.1.1729716557.6.1.1729718371.0.0.0; _ga=GA1.1.2096496035.1729565241"
            
            # Retrieve insights based on the quickInsightsType
            if quickInsightsType == "solar":
                res = EnergyController.__solarService.get_solar_insights(site_api_key, id)
            elif quickInsightsType == "electric":
                res = EnergyController.__portfolioService.get_electric_insights(id, cookie_string)
            elif quickInsightsType == "natural_gas":
                res = EnergyController.__portfolioService.get_gas_insights(id, cookie_string)
            else:
                return ReponseModel(message="Invalid insights type", status=400)
            
            # Check if response is empty
            if not res:
                return ReponseModel(message="No data available", status=200)

            return ReponseModel(message=res, status=200)
        except Exception as e:
            return ReponseModel(message=str(e), status=500)

