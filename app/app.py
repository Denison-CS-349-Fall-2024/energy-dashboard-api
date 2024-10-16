from flask import Flask
from fastapi import FastAPI
from main.controller.solarController import solar_bp


# create and configure the app
app = FastAPI()
# hook app with controllers
# app.register_blueprint(solar_bp)
app.include_router(solar_bp)


