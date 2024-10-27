import sys
import os

# Add the 'app' directory to the system path
import main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))
from main.service.solarService import solarService


def main():

    solar_service = solarService()

    # Set test parameters
    session_cookie = "<your_session_cookie>"
    property_ids = ["123", "456"]
    year = "2024"
    month = "10"

    # Test fetch_energy_data
    response = solar_service.fetch_energy_data(property_ids, session_cookie)
    print("Fetch Energy Data Response:", response.message)

    # Test call_m_function
    response = solar_service.call_m_function(property_ids, year, month, session_cookie)
    print("Call M Function Response:", response.message)

if __name__ == "__main__":
    main()
