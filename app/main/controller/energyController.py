from ..service.solarService import SolarService
from ..service.portfolioService import PortfolioService
from ..config.firebaseClient import FireBaseConfig
import requests, os, math
from dotenv import dotenv_values
from fastapi import APIRouter
from ..model.ReponseModel import ReponseModel
from ..model.BuildingDocument import BuildingDocument
 
energyController = APIRouter()
class EnergyController():
    __solarService = SolarService()
    __portfolioService = PortfolioService()
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

    @energyController.get('/site/{id}/quick_insights/')
    def get_quick_insights(id: int, quickInsightsType: str, session_cookie:str) -> ReponseModel:
        try:
            site_api_key = EnergyController.__firebaseClient.getFireStoreDB(
                EnergyController.__config["FIRESTORE_COLLECTION"],
                EnergyController.__config["FIRESTORE_SOLAR_DOCUMENT"]
            )["solarEdgeKey"]

            # Retrieve insights based on the quickInsightsType
            if quickInsightsType == "solar":
                res = EnergyController.__solarService.get_solar_insights(site_api_key, id)
            elif quickInsightsType == "electric":
                res = EnergyController.__portfolioService.get_electric_insights(id, session_cookie)
            elif quickInsightsType == "natural_gas":
                res = EnergyController.__portfolioService.get_gas_insights(id, session_cookie)
            else:
                return ReponseModel(message="Invalid insights type", status=400)
            
            # Check if response is empty
            if not res:
                return ReponseModel(message="No data available", status=200)

            return ReponseModel(message=res, status=200)
        except Exception as e:
            return ReponseModel(message=str(e), status=500)    

    @energyController.get('/get_chart_data/')
    def get_chart_data(property_id: int, chart_type: str, start_date: str, end_date: str, session_cookie: str) -> ReponseModel:
        """
        Fetches chart data for multiple properties based on the specified chart type and year.
        :param property_id: building ID.
        :param chart_type: The type of chart data ('d', 'm', 'y', 'all').
        :param chart_time: The time for which data is being requested.
        :param session_cookie: The session cookie string for authentication.
        :return: ReponseModel with chart data or error message.
        """
        try:
            #Get solar API key
            site_api_key = EnergyController.\
                __firebaseClient\
                .getFireStoreDB(EnergyController.__config["FIRESTORE_COLLECTION"],\
                                EnergyController.__config["FIRESTORE_SOLAR_DOCUMENT"])\
                                ["solarEdgeKey"]

            #Get building SolarId and PortfolioId. We need those id since the same building could have 2 different solarId and portfolioId
            data = EnergyController.__firebaseClient.\
                    getFireStoreDB(EnergyController.__config["FIRESTORE_BUILDING_RESOURCE_COLLECTION"],str(property_id))
            solarId, portfolioId = data.get("solar_edge_id"), data.get("portfolio_manager_id")

            # property_ids_list = property_ids.split(',')

            # Handle different chart types
            if chart_type == 'm':
                # Call the service function to get monthly data
                # solar = EnergyController.__solarService.call_m_function(property_ids_list, chart_time, session_cookie)
                return
            # Add logic for other chart types if needed
            elif chart_type == 'd':
                res = dict()
                if not math.isnan(solarId):
                    res["solar"] = EnergyController.__solarService.get_d_function(int(solarId), site_api_key, start_date, end_date)
                #if not math.isnan(portfolioId):
                #    res["electric"] = EnergyController.__portfolioService.get_d_function(int(portfolioId), session_cookie)
            elif chart_type == 'y':
                # Placeholder for yearly data handling
                res = {"error": "Yearly data fetching is not implemented yet."}
            elif chart_type == 'all':
                # Placeholder for fetching all data
                res = dict()
                if not math.isnan(solarId): 
                    res["solar"] = EnergyController.__solarService.solar_all_function(int(solarId), site_api_key)
                if not math.isnan(portfolioId): 
                    res["electric"] = EnergyController.__portfolioService.electric_all_function(int(portfolioId), session_cookie)
                    res["natural_gas"] = EnergyController.__portfolioService.natural_gas_all_function(int(portfolioId), session_cookie)
            else:
                return ReponseModel(message="Invalid chart type", status=400)

            # Check if the response is empty
            if not res:
                return ReponseModel(message="No data available", status=200)

            return ReponseModel(message=res, status=200)
        except Exception as e:
            return ReponseModel(message=str(e), status=500)
