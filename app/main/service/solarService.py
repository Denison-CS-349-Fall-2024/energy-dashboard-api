import requests, os
from dotenv import dotenv_values
from ..model.ReponseModel import ReponseModel
from ..model.BuildingInsight import BuildingInsight
from ..model.BuildingDocument import BuildingDocument


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
    
    # New function: Fetch energy data from EnergyStar for multiple properties
    def fetch_energy_data(self, property_ids, session_cookie):
        base_url = "https://portfoliomanager.energystar.gov/pm/property/{}/energyUsage/chart"
        headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Cookie": session_cookie,  # Use the provided cookie  
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }

        results = []
        for property_id in property_ids:
            url = base_url.format(property_id)
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Raise an error if the response status is not 200
                results.append({"property_id": property_id, "data": response.json()})
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data for property {property_id}: {e}")
                results.append({"property_id": property_id, "error": str(e)})

        return results  # Return a list of results for all properties

    # New function: Call 'month' function for multiple properties
    def call_m_function(self, property_ids, year, session_cookie):
        data_list = self.fetch_energy_data(property_ids, session_cookie)
        results = []

        for data_entry in data_list:
            property_id = data_entry.get('property_id')
            data = data_entry.get('data')
            
            if not data or data.get('noData', True):
                results.append({"property_id": property_id, "error": "No data available"})
                continue

            series_data = data.get('series', [])
            short_months = data.get('shortMonths', [])
            
            # Prepare sources data for each property
            sources = []
            for series in series_data:
                source_type = series.get('name').lower()
                if 'electric' in source_type:
                    sources.append({
                        "source": "electric",
                        "id": series.get('dataTypeId'),
                        "data": series.get('dataPoints', [])
                    })
                elif 'solar' in source_type:
                    sources.append({
                        "source": "solar",
                        "id": series.get('dataTypeId'),
                        "data": series.get('dataPoints', [])
                    })
                elif 'natural gas' in source_type:
                    sources.append({
                        "source": "natural_gas",
                        "id": series.get('dataTypeId'),
                        "data": series.get('dataPoints', [])
                    })

            response = {
                "property_id": property_id,
                "chart_type": "m",
                "chart_time": year,
                "sources": sources
            }
            results.append(response)

        return results  
        
#       

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
