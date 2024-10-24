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

    @energyController.get('/get_chart_data/')
    def get_chart_data(property_ids: str, chart_type: str, year: str, session_cookie: str) -> ReponseModel:
        """
        Fetches chart data for multiple properties based on the specified chart type and year.
        :param property_ids: Comma-separated list of property IDs.
        :param chart_type: The type of chart data ('d', 'm', 'y', 'all').
        :param year: The year for which data is being requested.
        :param session_cookie: The session cookie string for authentication.
        :return: ReponseModel with chart data or error message.
        """
        try:
            # Split property_ids into a list
            property_ids_list = property_ids.split(',')

            # Handle different chart types
            if chart_type == 'm':
                # Call the service function to get monthly data
                res = EnergyController.__solarService.call_m_function(property_ids_list, year, session_cookie)

            # Add logic for other chart types if needed
            elif chart_type == 'd':
                # Placeholder for daily data handling
                res = {"error": "Daily data fetching is not implemented yet."}
            elif chart_type == 'y':
                # Placeholder for yearly data handling
                res = {"error": "Yearly data fetching is not implemented yet."}
            elif chart_type == 'all':
                # Placeholder for fetching all data
                res = {"error": "Fetching all data is not implemented yet."}
            else:
                return ReponseModel(message="Invalid chart type", status=400)

            # Check if the response is empty
            if not res:
                return ReponseModel(message="No data available", status=200)

            return ReponseModel(message=res, status=200)
        except Exception as e:
            print(f"Error in get_chart_data: {e}")
            return ReponseModel(message=str(e), status=500)
