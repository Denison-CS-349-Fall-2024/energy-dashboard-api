import requests, os
from dotenv import dotenv_values
from ..model.ReponseModel import ReponseModel


class PortfolioService:
    __config = dotenv_values(os.getcwd() + "/.env")

    def __init__(self):
        self.domain = PortfolioService.__config["PORTFOLIO_URL"]

    def get_electric_insights(self, property_id: int, cookie_string: str) -> ReponseModel:
        # Corrected URL with no extra slash
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
                if data.get("noData") or not data.get("series"):
                    return ReponseModel(message="No electric data available", status=200)

                # Look for the data series with "dataTypeId": 1 (Electric - Grid)
                electric_series = next(
                    (series for series in data["series"] if series["dataTypeId"] == 1),
                    None
                )

                if electric_series:
                    # Extract the monthly electric data
                    electric_data = electric_series.get("data", [])
                    return ReponseModel(
                        message={
                            "consumption": electric_data,
                            "unit": data.get("yAxisName", "kBtu")
                        },
                        status=200
                    )

                return ReponseModel(message="Electric data series not found", status=200)

            return ReponseModel(message="Failed to retrieve electric data", status=response.status_code)

        except requests.exceptions.RequestException as e:
            return ReponseModel(message=f"Error fetching electric data: {str(e)}", status=500)

    def get_gas_insights(self, property_id: int, cookie_string: str) -> ReponseModel:
        # Corrected URL with no extra slash
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
                if data.get("noData") or not data.get("series"):
                    return ReponseModel(message="No natural gas data available", status=200)

                # Look for the data series with "dataTypeId": 2 (Natural Gas)
                gas_series = next(
                    (series for series in data["series"] if series["dataTypeId"] == 2),
                    None
                )

                if gas_series:
                    # Extract the monthly gas data
                    gas_data = gas_series.get("data", [])
                    return ReponseModel(
                        message={
                            "consumption": gas_data,
                            "unit": data.get("yAxisName", "kBtu")
                        },
                        status=200
                    )

                return ReponseModel(message="Natural gas data series not found", status=200)

            return ReponseModel(message="Failed to retrieve natural gas data", status=response.status_code)

        except requests.exceptions.RequestException as e:
            return ReponseModel(message=f"Error fetching natural gas data: {str(e)}", status=500)
