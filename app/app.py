from fastapi import FastAPI
from main.controller.solarController import solarController
from main.controller.fireStoreController import firebaseController

# create and configure the app
app = FastAPI()
# hook app with controllers
app.include_router(solarController)
app.include_router(firebaseController)