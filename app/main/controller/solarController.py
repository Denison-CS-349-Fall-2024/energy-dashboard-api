from flask import request
from flask import Blueprint, jsonify, Response
from ..service.solarService import SolarService
from ..config.firebaseClient import FireBaseConfig
import requests, os
from dotenv import dotenv_values

solar_bp = Blueprint('solar_bp', __name__)
class SolarArrayController():
    __solarService = SolarService()
    __firebaseClient = FireBaseConfig()
    __config = dotenv_values(os.getcwd()+"/.env")

    @solar_bp.route('/sites/list/')
    def get_site_by_key()->Response:
        try:
            site_api_key = SolarArrayController.\
                __firebaseClient\
                .getFireStoreDB(SolarArrayController.__config["FIRESTORE_COLLECTION"],\
                                SolarArrayController.__config["FIRESTORE_SOLAR_DOCUMENT"])\
                                ["solarEdgeKey"]
            res = SolarArrayController.__solarService.get_site_by_key(site_api_key)
            if not res:
                return Response(None, 200)
            return res
        except:
            return Response(str(requests.exceptions.HTTPError),500)
        
    @solar_bp.route('/site/<site_id>/power')
    def get_site_power(site_id):
        try:
            site_api_key = SolarArrayController.\
                __firebaseClient\
                .getFireStoreDB(SolarArrayController.__config["FIRESTORE_COLLECTION"],\
                                SolarArrayController.__config["FIRESTORE_SOLAR_DOCUMENT"])\
                                ["solarEdgeKey"]
            startTime = request.args.get("startTime")
            endTime = request.args.get("endTime")
            res = SolarArrayController.__solarService.get_site_power(site_api_key,startTime,endTime,site_id)
            if not res:
                return Response(None, 200)
            return res
        except:
            return Response(str(requests.exceptions.HTTPError),500)
        
    @solar_bp.route('/site/<site_id>/energy')
    def get_site_energy(site_id):
        try:
            site_api_key = SolarArrayController.\
                __firebaseClient\
                .getFireStoreDB(SolarArrayController.__config["FIRESTORE_COLLECTION"],\
                                SolarArrayController.__config["FIRESTORE_SOLAR_DOCUMENT"])\
                                ["solarEdgeKey"]
            startDate = request.args.get("startDate")
            endDate = request.args.get("endDate")
            timeUnit = request.args.get("timeUnit")
            res = SolarArrayController.__solarService.get_site_energy(site_api_key,startDate,endDate,timeUnit,site_id)
            if not res:
                return Response(None, 200)
            return res
        except:
            return Response(str(requests.exceptions.HTTPError),500)