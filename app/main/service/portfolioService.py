import requests, os
from datetime import datetime
from dotenv import dotenv_values
from ..model.ReponseModel import ReponseModel
from ..model.BuildingInsight import BuildingInsight
from ..model.PortfolioEnergy import PortfolioEnergy

class PortfolioService:
    __config = dotenv_values(os.getcwd() + "/.env")

    def __init__(self):
        self.domain = PortfolioService.__config["PORTFOLIO_URL"]

    def convert_epoch_to_date_string(self, epoch_time: int):
        """
        Converts an epoch time (in milliseconds) to a human-readable date string.
        """
        epoch_seconds = epoch_time / 1000
        date_time = datetime.utcfromtimestamp(epoch_seconds)
        return date_time
    
    #electric + gas use the same API call
    def get_portfolio_energy_usage(self,session_cookie,property_id)->ReponseModel:
        url = f"{self.domain}pm/property/{property_id}/energyUsage/chart"
        headers = {
            "Content-Type": "application/json",
            "Cookie": session_cookie
        }
        try:
            # Make the GET request to the Energy Star API
            response = requests.get(url, headers=headers)
            # Handle the response=
            if response.status_code == 200:
                data = response.json()
                return ReponseModel(message=data,status=200)
            return ReponseModel(message="Portfolio API error", status=500)
        except:
            return ReponseModel(message=requests.exceptions.HTTPError,status=500)

    def get_energy_data(self, session_cookie, property_id, energyType):
        #get portfolio data -> list of datapoint with entire time span [List]
        response = self.get_portfolio_energy_usage(session_cookie,property_id)
        if not response.message.get("series"):
            return None
        else:
            #filter
            energyDataAll,energyData = response.message.get("series"),None
            if energyType=="electric":
                for energy in energyDataAll:
                    if energy.get("dataTypeId")==1: 
                        energyData = energy
            else:
                for energy in energyDataAll:
                    if energy.get("dataTypeId")==2: 
                        energyData = energy
            if not energyData: 
                return None
            #preprocess 
            energyDataCollection = dict()
            for dataPoint in energyData.get("data"):
                epochTime = dataPoint[0]
                dataTime = self.convert_epoch_to_date_string(epochTime)
                yearTime,monthTime = dataTime.year, dataTime.month
                if yearTime not in energyDataCollection: 
                    energyDataCollection[yearTime]=dict()
                    if monthTime not in energyDataCollection[yearTime]:
                        energyDataCollection[yearTime][monthTime]=dataPoint[1]
                energyDataCollection[yearTime][monthTime]=dataPoint[1]
            return energyDataCollection

    def get_electric_insights(self, property_id: int, cookie_string: str) -> BuildingInsight:
        url = f"{self.domain}pm/property/{property_id}/energyUsage/chart"
        headers = {
            "Content-Type": "application/json",
            "Cookie": cookie_string
        }

        try:
            # Make the GET request to the Energy Star API
            response = requests.get(url, headers=headers)

            # Handle the response
            if response.status_code == 200:
                data = response.json()

                # Check if there is data and if the series contains electric data
                if not data.get("series"):
                    return BuildingInsight(
                        id=property_id,
                        installed_on="N/A",
                        lifetime_energy="0",
                        recent_month_energy="0",
                        energy_unit="kBtu"
                    )

                # Look for the data series with "dataTypeId": 1 (Electric - Grid)
                electric_series = next(
                    (series for series in data["series"] if series["dataTypeId"] == 1),
                    None
                )

                if electric_series:
                    # Extract the monthly electric data
                    electric_data = electric_series.get("data", [])

                    # Get `installed_on` as the first timestamp
                    installed_on = (
                        str(self.convert_epoch_to_date_string(electric_data[0][0]))
                        if electric_data else "N/A"
                    )

                    # Get `recentMonthEnergy` as the last value
                    recent_month_energy = str(electric_data[-1][1]) if electric_data else "0"

                    # Calculate `lifetimeEnergy` as the sum of all energy values
                    lifetime_energy = str(sum(point[1] for point in electric_data))

                    # Create a BuildingInsight instance with the extracted data
                    return BuildingInsight(
                        id=property_id,
                        installed_on=installed_on,
                        lifetime_energy=lifetime_energy,
                        recent_month_energy=recent_month_energy,
                        energy_unit="kBtu"
                    )

            # Return a default BuildingInsight instance in case of failure
            return BuildingInsight(
                id=property_id,
                installed_on="N/A",
                lifetime_energy="0",
                recent_month_energy="0",
                energy_unit="kBtu"
            )

        except requests.exceptions.RequestException as e:
            return BuildingInsight(
                id=property_id,
                installed_on="N/A",
                lifetime_energy="0",
                recent_month_energy="0",
                energy_unit="kBtu"
            )

    def get_gas_insights(self, property_id: int, cookie_string: str) -> BuildingInsight:
        url = f"{self.domain}pm/property/{property_id}/energyUsage/chart"
        headers = {
            "Content-Type": "application/json",
            "Cookie": cookie_string
        }

        try:
            # Make the GET request to the Energy Star API
            response = requests.get(url, headers=headers)

            # Handle the response
            if response.status_code == 200:
                data = response.json()

                # Check if there is data and if the series contains gas data
                if not data.get("series"):
                    return BuildingInsight(
                        id=property_id,
                        installed_on="N/A",
                        lifetime_energy="0",
                        recent_month_energy="0",
                        energy_unit="kBtu"
                    )

                # Look for the data series with "dataTypeId": 2 (Natural Gas)
                gas_series = next(
                    (series for series in data["series"] if series["dataTypeId"] == 2),
                    None
                )

                if gas_series:
                    # Extract the monthly gas data
                    gas_data = gas_series.get("data", [])

                    # Get `installed_on` as the first timestamp
                    installed_on = (
                        str(self.convert_epoch_to_date_string(gas_data[0][0]))
                        if gas_data else "N/A"
                    )

                    # Get `recentMonthEnergy` as the last value
                    recent_month_energy = str(gas_data[-1][1]) if gas_data else "0"

                    # Calculate `lifetimeEnergy` as the sum of all energy values
                    lifetime_energy = str(sum(point[1] for point in gas_data))

                    # Create a BuildingInsight instance with the extracted data
                    return BuildingInsight(
                        id=property_id,
                        installed_on=installed_on,
                        lifetime_energy=lifetime_energy,
                        recent_month_energy=recent_month_energy,
                        energy_unit="kBtu"
                    )

            # Return a default BuildingInsight instance in case of failure
            return BuildingInsight(
                id=property_id,
                installed_on="N/A",
                lifetime_energy="0",
                recent_month_energy="0",
                energy_unit="kBtu"
            )

        except requests.exceptions.RequestException as e:
            return BuildingInsight(
                id=property_id,
                installed_on="N/A",
                lifetime_energy="0",
                recent_month_energy="0",
                energy_unit="kBtu"
            )
        
    def electric_all_function(self, property_id, session_cookie) -> ReponseModel: 
        energyResponse= {"id": property_id}
        try:
            energyYear = self.get_energy_data(session_cookie,property_id,"electric")
            energyResponse["data"] = energyYear
            return ReponseModel(message=energyResponse, status=200)
        except:
            return ReponseModel(message=str(requests.exceptions.HTTPError),status=500)
        
    def natural_gas_all_function(self, property_id, session_cookie) -> ReponseModel: 
        energyResponse= {"id": property_id}
        try:
            energyYear = self.get_energy_data(session_cookie,property_id,"natural_gas")
            energyResponse["data"] = energyYear
            return ReponseModel(message=energyResponse, status=200)
        except:
            return ReponseModel(message=str(requests.exceptions.HTTPError),status=500)