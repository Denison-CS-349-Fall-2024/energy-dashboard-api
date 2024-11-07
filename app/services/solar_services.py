import json
from datetime import date
from typing import Optional

import aiohttp

from app.config import settings
from app.helpers.helpers import (
    TIME_UNIT_MAPPING,
    infer_start_and_end_date_from_chart_type_and_chart_date,
)
from app.schemas import ChartType


class SolarService:
    def __init__(self):
        self.api_key = settings.API_KEY_SOLAR_EDGE
        self.base_url = "https://monitoringapi.solaredge.com"

    async def get_site_details(self, site_id: int):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/site/{site_id}/details"
            params = {"api_key": self.api_key}
            async with session.get(url, params=params) as response:
                response.raise_for_status()  # Raise an error for bad responses
                return await response.json()

    async def get_site_overview(self, site_id: int):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/site/{site_id}/overview"
            params = {"api_key": self.api_key}
            async with session.get(url, params=params) as response:
                response.raise_for_status()  # Raise an error for bad responses
                return await response.json()

    async def get_site_energy(
        self, site_id: int, chart_type: ChartType, chart_date: Optional[date] = None
    ):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/site/{site_id}/energy"
            start_date, end_date = (
                infer_start_and_end_date_from_chart_type_and_chart_date(
                    chart_type, chart_date
                )
            )
            params = {
                "api_key": self.api_key,
                "timeUnit": TIME_UNIT_MAPPING[chart_type],
                "startDate": start_date,
                "endDate": end_date,
            }
            async with session.get(url, params=params) as response:
                response.raise_for_status()  # Raise an error for bad responses
                return await response.json()

    async def get_all_sites(self):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/sites/list"
            params = {"api_key": self.api_key, "size": 5000}
            async with session.get(url, params=params) as response:
                response.raise_for_status()  # Raise an error for bad responses
                json_in_text = await response.text()
                return json.loads(json_in_text)
    
    async def get_env_benefit(self, site_id:int, data_lock, share_data):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/site/{site_id}/envBenefits?systemUnits=Imperial"
            params = {"api_key": self.api_key, "size": 5000}
            try:
                async with session.get(url, params=params) as response:
                    json_in_text = await response.text()
                    json_dict = json.loads(json_in_text)
                    async with data_lock:
                        if "envBenefits" in json_dict:
                            share_data["Co2EmissionSaved"]+=json_dict.get("envBenefits").get("gasEmissionSaved").get("co2")
                            share_data["treesPlanted"]+=json_dict.get("envBenefits").get("treesPlanted")
            except Exception as e:
                #keep calculating + avoid hard stor from having exception
                print('some site_id might not have access to SolarEdge', e)


solar_service = SolarService()
