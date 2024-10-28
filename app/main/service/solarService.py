import requests, os
from dotenv import dotenv_values
from ..model.ReponseModel import ReponseModel
from ..model.BuildingInsight import BuildingInsight
from ..model.BuildingDocument import BuildingDocument
from datetime import date

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

    def get_site_energy_detail(self,api_key,startDate,endDate,timeUnit,site_id)->ReponseModel:
        params = {"api_key": api_key, "startDate": startDate, "endDate": endDate, "timeUnit": timeUnit}
        try:
            res = requests.get(self.domain+f"site/{site_id}/energyDetails",params=params)
            if res.status_code==200:
                return ReponseModel(message=res.json(),status=200)
            return ReponseModel(message="Unauthorized",status=401)
        except:
            return ReponseModel(message=str(requests.exceptions.HTTPError),status=500)
        

    def get_solar_insights(self, api_key: str, site_id: int) -> BuildingInsight:
        params = {"api_key": api_key}

        try:
            # Call 1: Get site details (to retrieve the installation date)
            site_details_res = requests.get(f"{self.domain}/site/{site_id}/details", params=params)
            installed_on = "N/A"  # Default value in case data is not available
            if site_details_res.status_code == 200:
                # Extract the 'installationDate' from the 'details' object in the response
                details = site_details_res.json().get("details", {})
                installed_on = details.get("installationDate", "N/A")

            # Call 2: Get site overview (to retrieve lifetime and recent month energy)
            site_overview_res = requests.get(f"{self.domain}/site/{site_id}/overview", params=params)
            lifetime_energy = "0"
            recent_month_energy = "0"
            energy_unit = "Wh"  # Assuming the unit is Wh as default

            if site_overview_res.status_code == 200:
                overview = site_overview_res.json().get("overview", {})

                # Extract lifetime energy and recent month's energy from the overview data
                lifetime_energy = str(overview.get("lifeTimeData", {}).get("energy", "0"))
                recent_month_energy = str(overview.get("lastMonthData", {}).get("energy", "0"))

            # Create an instance of BuildingInsight with the retrieved data
            insights_data = BuildingInsight(
                id=site_id,
                installed_on=installed_on,
                lifetime_energy=lifetime_energy,
                recent_month_energy=recent_month_energy,
                energy_unit=energy_unit
            )

            return insights_data

        except requests.exceptions.RequestException as e:
            # Handle general request exceptions and provide a meaningful error message
            raise ValueError(f"Failed to retrieve insights for site {site_id}: {str(e)}")       

    def solar_all_function(self,property_id, api_key)->ReponseModel:
        quickInsight = self.get_solar_insights(api_key,property_id)
        installTime = quickInsight.installed_on
        res = self.get_site_energy(api_key,installTime,str(date.today()),"YEAR",property_id)
        return res.message

    def get_d_function(self, property_id, api_key, start_date, end_date)->ReponseModel:
        res = self.get_site_energy_detail(api_key, start_date, end_date, "QUARTER_OF_AN_HOUR", property_id)
        return res.message