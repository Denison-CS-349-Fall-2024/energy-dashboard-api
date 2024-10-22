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

    def get_solar_insights(self, api_key: str, site_id: int) -> dict:
        params = {"api_key": api_key}
        
        try:
            # Call 1: Get site details (to retrieve the installation date)
            site_details_res = requests.get(f"{self.domain}/site/{site_id}/details", params=params)
            installed_on = None
            if site_details_res.status_code == 200:
                # Extract the 'installationDate' from the 'details' object in the response
                details = site_details_res.json().get("details", {})
                installed_on = details.get("installationDate")

            # Call 2: Get site overview (to retrieve lifetime and recent month energy)
            site_overview_res = requests.get(f"{self.domain}/site/{site_id}/overview", params=params)
            lifetime_energy = None
            recent_month_energy = None
            energy_unit = "kWh"  # Assuming the unit is kWh as default
            if site_overview_res.status_code == 200:
                overview = site_overview_res.json().get("overview", {})
                
                # Extract lifetime energy and recent month's energy from the overview data
                lifetime_energy = overview.get("lifeTimeData", {}).get("energy")
                recent_month_energy = overview.get("lastMonthData", {}).get("energy")

            # Combine all the retrieved data into the insights dictionary
            insights_data = {
                "id": site_id,
                "installedOn": installed_on,
                "lifetimeEnergy": lifetime_energy,
                "recentMonthEnergy": recent_month_energy,
                "energyUnit": energy_unit
            }

            return insights_data

        except requests.exceptions.HTTPError as e:
            # Return the error message in case of a request failure
            return {"error": str(e), "status": 500}
