import json

import aiohttp


class EnergyStarService:
    def __init__(self):
        self.base_url = "https://portfoliomanager.energystar.gov"

    async def get_energy_usage(self, site_id, selenium_session_cookie):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/pm/property/{site_id}/energyUsage/chart"
            headers = {
                "Content-Type": "application/json",
                "Cookie": selenium_session_cookie,
            }
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()  # Raise an error for bad responses
                json_in_text = await response.text()
                return json.loads(json_in_text)


energystar_service = EnergyStarService()
