from fastapi import FastAPI, Query
from main.controller.energyController import energyController
from main.controller.fireStoreController import firebaseController
from fastapi.exceptions import HTTPException
from fastapi.testclient import TestClient

# create and configure the app
app = FastAPI()
# hook app with controllers
app.include_router(energyController)
app.include_router(firebaseController)

client = TestClient(app)  # Create a test client for the FastAPI app

# Define the get_chart_data endpoint directly in FastAPI
@app.get("/energy/get_chart_data/")
async def chart_data(
    property_ids: str = Query(..., description="Comma-separated list of property IDs"),
    chart_type: str = Query(..., description="Type of chart data ('d', 'm', 'y', 'all')"),
    year: str = Query(..., description="The year for which data is being requested"),
    session_cookie: str = Query(..., description="Session cookie for authentication")
):
    """
    Endpoint to fetch chart data for multiple properties based on the specified parameters.
    """
    # Split property_ids into a list
    property_ids_list = property_ids.split(',')

    # # Prepare request dictionary
    # request_dict = {
    #     "chart_type": chart_type,
    #     "property_ids": property_ids_list,
    #     "year": year,
    #     "session_cookie": session_cookie
    # }

    # # Call the get_chart_data function from energyController
    # response = get_chart_data(request_dict)

    # return response

     # Prepare request parameters for internal call
    params = {
        "property_ids": property_ids,
        "chart_type": chart_type,
        "year": year,
        "session_cookie": session_cookie
    }

    # Make an internal call to the /get_chart_data/ endpoint
    response = client.get("/energy/get_chart_data/", params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return response.json()