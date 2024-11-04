import asyncio
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from firebase_admin import firestore

from app.helpers.helpers import (
    format_solar_edge_data,
    infer_energy_star_data,
    infer_quick_insights_from_energy_star_data,
    infer_quick_insights_from_solar_edge_data,
)
from app.services.energystar_services import energystar_service
from app.services.solar_services import solar_service

from ..db import db
from ..schemas import ChartData, ChartType, QuickInsights, QuickInsightsType, Site

router = APIRouter()


@router.get("/sites", response_model=List[Site])
async def read_sites():
    docs = db.collection("sites").stream()

    sites = [{"id": doc.id, **doc.to_dict()} async for doc in docs]
    return sites


@router.get("/quick_insights", response_model=QuickInsights)
async def quick_insights(id: str, type: QuickInsightsType):
    doc = await db.collection("sites").document(id).get()
    if not doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find site id {id}",
        )

    site_info = doc.to_dict()
    if type == QuickInsightsType.solar:
        if not site_info["id_solar_edge"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"QuickInsightsType solar is not available for this site id {id}",
            )

        tasks = [
            solar_service.get_site_details(site_info["id_solar_edge"]),
            solar_service.get_site_overview(site_info["id_solar_edge"]),
        ]
        site_details, site_overview = await asyncio.gather(*tasks)
        response = infer_quick_insights_from_solar_edge_data(
            site_details, site_overview
        )
    else:
        if not site_info["id_energy_star"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"QuickInsightsType electric / natural_gas is not available for this site id {id}",
            )
        results = await (
            db.collection("cookies")
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(1)
            .get()
        )
        selenium_session_cookie = results[0].to_dict()["cookie"]
        result = await energystar_service.get_energy_usage(
            site_info["id_energy_star"], selenium_session_cookie
        )
        response = infer_quick_insights_from_energy_star_data(result, type)

    response.update(
        {
            "id": id,
            "id_solar_edge": site_info["id_solar_edge"],
            "id_energy_star": site_info["id_energy_star"],
        }
    )
    return response


@router.get("/chart_data", response_model=ChartData)
async def chart_data(
    id: str,
    chart_type: ChartType,
    chart_date: Optional[date] = None,
):
    doc = await db.collection("sites").document(id).get()
    if not doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find site id {id}",
        )

    site_info = doc.to_dict()
    response = {
        "id": id,
        "id_solar_edge": site_info["id_solar_edge"],
        "id_energy_star": site_info["id_energy_star"],
        "chart_type": chart_type,
        "chart_date": chart_date,
        "sources": [],
    }

    if site_info["id_solar_edge"]:
        solar_edge_data = await solar_service.get_site_energy(
            site_info["id_solar_edge"], chart_type, chart_date
        )
        response["sources"].extend(format_solar_edge_data(solar_edge_data))

    if site_info["id_energy_star"] and (
        chart_type == ChartType.All or chart_type == ChartType.Y
    ):
        results = await (
            db.collection("cookies")
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(1)
            .get()
        )
        selenium_session_cookie = results[0].to_dict().get("cookie")
        energy_star_data = await energystar_service.get_energy_usage(
            site_info["id_energy_star"], selenium_session_cookie
        )
        response["sources"].extend(
            infer_energy_star_data(energy_star_data, chart_date, chart_type)
        )

    return response
