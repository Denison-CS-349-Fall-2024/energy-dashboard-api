import json
from datetime import date
from typing import Optional

import aiohttp
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.helpers.helpers import (
    TIME_UNIT_MAPPING,
    infer_start_and_end_date_from_chart_type_and_chart_date,
)
from app.schemas import ChartType


class SolarService:
    def __init__(self):
        self.base_url = "https://monitoringapi.solaredge.com"

    @retry(
        retry=retry_if_exception(Exception),
        stop=stop_after_attempt(5),  # Stop retrying after 5 attempts
        wait=wait_exponential(
            multiplier=1, min=1, max=10
        ),  # Exponential backoff: 1s, 2s, 4s...
    )
    async def get_all_sites(self, custom_api_key: str):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/sites/list"
            params = {"api_key": custom_api_key, "size": 5000}
            async with session.get(url, params=params) as response:
                response.raise_for_status()  # Raise an error for bad responses
                json_in_text = await response.text()
                return json.loads(json_in_text)

    @retry(
        retry=retry_if_exception(Exception),
        stop=stop_after_attempt(5),  # Stop retrying after 5 attempts
        wait=wait_exponential(
            multiplier=1, min=1, max=10
        ),  # Exponential backoff: 1s, 2s, 4s...
    )
    async def get_site_details(self, site_id: int, custom_api_key: str):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/site/{site_id}/details"
            params = {"api_key": custom_api_key}
            async with session.get(url, params=params) as response:
                response.raise_for_status()  # Raise an error for bad responses
                return await response.json()

    @retry(
        retry=retry_if_exception(Exception),
        stop=stop_after_attempt(5),  # Stop retrying after 5 attempts
        wait=wait_exponential(
            multiplier=1, min=1, max=10
        ),  # Exponential backoff: 1s, 2s, 4s...
    )
    async def get_site_overview(self, site_id: int, custom_api_key: str):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/site/{site_id}/overview"
            params = {"api_key": custom_api_key}
            async with session.get(url, params=params) as response:
                response.raise_for_status()  # Raise an error for bad responses
                return await response.json()

    @retry(
        retry=retry_if_exception(Exception),
        stop=stop_after_attempt(5),  # Stop retrying after 5 attempts
        wait=wait_exponential(
            multiplier=1, min=1, max=10
        ),  # Exponential backoff: 1s, 2s, 4s...
    )
    async def get_sites_energy(
        self,
        id_solar_edge_list: list[int],
        custom_api_key: str,
        chart_type: ChartType,
        chart_date: Optional[date] = None,
    ):
        async with aiohttp.ClientSession() as session:
            # should have no duplicate ids
            id_solar_edge_list_in_string = ",".join(
                str(i) for i in set(id_solar_edge_list)
            )
            start_date, end_date = (
                infer_start_and_end_date_from_chart_type_and_chart_date(
                    chart_type, chart_date
                )
            )
            url = f"{self.base_url}/sites/{id_solar_edge_list_in_string}/energy"
            params = {
                "api_key": custom_api_key,
                "timeUnit": TIME_UNIT_MAPPING[chart_type],
                "startDate": start_date,
                "endDate": end_date,
            }
            async with session.get(url, params=params) as response:
                response.raise_for_status()  # Raise an error for bad responses
                json_in_text = await response.text()
                return json.loads(json_in_text)

    @retry(
        retry=retry_if_exception(Exception),
        stop=stop_after_attempt(5),  # Stop retrying after 5 attempts
        wait=wait_exponential(
            multiplier=1, min=1, max=10
        ),  # Exponential backoff: 1s, 2s, 4s...
    )
    async def get_env_benefits(self, id_solar_edge: int, custom_api_key: str):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/site/{id_solar_edge}/envBenefits"
            params = {
                "api_key": custom_api_key,
                "systemUnits": "Imperial",
            }
            async with session.get(url, params=params) as response:
                response.raise_for_status()  # Raise an error for bad responses
                return await response.json()


solar_service = SolarService()
