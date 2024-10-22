import requests, os
from flask import Response
from dotenv import dotenv_values
from ..model.ReponseModel import ReponseModel

class SolarService:
    __config = dotenv_values(os.getcwd()+"/.env")
    def __init__(self):
        self.domain = SolarService.__config["SOLAR_ARRAY_URL"]
        
    def get_site_by_key(self,api_key)->ReponseModel:
        params = {"api_key": api_key}
        try:
            res = requests.get(self.domain+"sites/list", params=params)
            if res.status_code==200:
                return ReponseModel(message=res.json(),status=200)
            return ReponseModel(message="Unauthorized",status=401)
        except:
            return ReponseModel(message=str(requests.exceptions.HTTPError),status=500)
    
    def get_site_power(self,api_key,startTime,endTime,site_id)->ReponseModel:
        params = {"api_key": api_key, "startTime": startTime, "endTime": endTime}
        try:
            res = requests.get(self.domain+f"site/{site_id}/power",params=params)
            if res.status_code==200:
                return ReponseModel(message=res.json(),status=200)
            return ReponseModel(message="Unauthorized",status=401)
        except:
            return ReponseModel(str(requests.exceptions.HTTPError),status=500)
    
    def get_site_energy(self,api_key,startDate,endDate,timeUnit,site_id)->ReponseModel:
        params = {"api_key": api_key, "startDate": startDate, "endDate": endDate, "timeUnit": timeUnit}
        try:
            res = requests.get(self.domain+f"site/{site_id}/energy",params=params)
            if res.status_code==200:
                return ReponseModel(message=res.json(),status=200)
            return ReponseModel(message="Unauthorized",status=401)
        except:
            return ReponseModel(message=str(requests.exceptions.HTTPError),status=500)
        