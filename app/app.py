from fastapi import FastAPI
from main.controller.energyController import energyController
from main.controller.fireStoreController import firebaseController

# create and configure the app
app = FastAPI()
# hook app with controllers
app.include_router(energyController)
app.include_router(firebaseController)