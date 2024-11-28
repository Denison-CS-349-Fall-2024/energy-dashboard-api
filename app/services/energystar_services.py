import json
import time

import aiohttp
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential


class EnergyStarService:
    def __init__(self):
        self.base_url = "https://portfoliomanager.energystar.gov"

    def retry_if_calculation_in_progress(exception):
        return (
            isinstance(exception, ValueError)
            and str(exception) == "CALCULATION_IN_PROGRESS"
        )

    async def force_compute(self, site_id, selenium_session_cookie):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/pm/property/{site_id}/energyUsage/chart/compute?_={int(time.time() * 1000)}"
            headers = {
                "Cookie": selenium_session_cookie,
            }
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()  # Raise an error for bad responses
                empty_text = await response.text()
                return empty_text

    @retry(
        retry=retry_if_exception(retry_if_calculation_in_progress),
        stop=stop_after_attempt(5),  # Stop retrying after 5 attempts
        wait=wait_exponential(
            multiplier=1, min=1, max=10
        ),  # Exponential backoff: 1s, 2s, 4s...
    )
    async def get_energy_usage(self, site_id, selenium_session_cookie):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/pm/property/{site_id}/energyUsage/chart?_={int(time.time() * 1000)}"
            headers = {
                "Content-Type": "application/json",
                "Cookie": selenium_session_cookie,
            }
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()  # Raise an error for bad responses
                json_in_text = await response.text()
                json_data = json.loads(json_in_text)
                if json_data["jobStatus"] != "COMPLETE_WITH_DATA":
                    raise ValueError("CALCULATION_IN_PROGRESS")
                return json_data


energystar_service = EnergyStarService()
