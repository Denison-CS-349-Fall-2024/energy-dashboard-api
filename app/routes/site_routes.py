import asyncio
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Body, HTTPException, status
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.db import db
from app.helpers.helpers import (
    format_solar_edge_data,
    infer_energy_star_data,
    infer_quick_insights_from_energy_star_data,
    infer_quick_insights_from_solar_edge_data,
)
from app.schemas import (
    ChartData,
    ChartType,
    EnvBenefitsData,
    QuickInsights,
    QuickInsightsType,
    Site,
    UploadedSolarEdgeSite,
)
from app.services.energystar_services import energystar_service
from app.services.solar_services import solar_service

router = APIRouter()


@router.get("/sites", response_model=List[Site])
async def read_sites():
    docs = db.collection("sites").stream()

    sites = [{"id": doc.id, **doc.to_dict()} async for doc in docs]
    return sites


@router.get("/quick_insights", response_model=QuickInsights)
async def get_quick_insights(id: str, type: QuickInsightsType):
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
            solar_service.get_site_details(
                site_info["id_solar_edge"], site_info["custom_api_key"]
            ),
            solar_service.get_site_overview(
                site_info["id_solar_edge"], site_info["custom_api_key"]
            ),
        ]
        site_details, site_overview = await asyncio.gather(*tasks)
        response = infer_quick_insights_from_solar_edge_data(
            site_details, site_overview
        )
    else:
        if not site_info["id_energy_star"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"QuickInsightsType electric_grid / natural_gas is not available for this site id {id}",
            )
        results = await (
            db.collection("cookies")
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(1)
            .get()
        )
        selenium_session_cookie = results[0].to_dict()["cookie"]
        await energystar_service.force_compute(
            site_info["id_energy_star"], selenium_session_cookie
        )
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
async def get_chart_data(
    id: str,
    chart_type: ChartType,
    chart_date: Optional[date] = None,
):
    response = {}
    site_info = {}
    if id == "campus_data":
        response = {
            "id": "campus_data",
            "id_solar_edge": None,
            "id_energy_star": 28509337,
            "chart_type": chart_type,
            "chart_date": chart_date,
            "sources": [],
        }
    else:
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

    if id == "campus_data":
        sites = await read_sites()
        solar_edge_sites = [site for site in sites if site["id_solar_edge"]]

        tasks = [
            solar_service.get_sites_energy(
                [solar_edge_site["id_solar_edge"]],
                solar_edge_site["custom_api_key"],
                chart_type=chart_type,
                chart_date=chart_date,
            )
            for solar_edge_site in solar_edge_sites
        ]
        results = await asyncio.gather(*tasks)
        response["sources"].extend(format_solar_edge_data(results))

    if response["id_solar_edge"]:
        solar_edge_data = await solar_service.get_sites_energy(
            [response["id_solar_edge"]],
            site_info["custom_api_key"],
            chart_type,
            chart_date,
        )
        response["sources"].extend(format_solar_edge_data([solar_edge_data]))

    if response["id_energy_star"] and (
        chart_type == ChartType.All or chart_type == ChartType.Y
    ):
        results = await (
            db.collection("cookies")
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(1)
            .get()
        )
        selenium_session_cookie = results[0].to_dict().get("cookie")
        await energystar_service.force_compute(
            response["id_energy_star"], selenium_session_cookie
        )
        energy_star_data = await energystar_service.get_energy_usage(
            response["id_energy_star"], selenium_session_cookie
        )
        response["sources"].extend(
            infer_energy_star_data(energy_star_data, chart_date, chart_type)
        )

    return response


@router.get("/campus_env_benefits", response_model=EnvBenefitsData)
async def get_campus_env_benefits():
    sites = await read_sites()
    solar_edge_sites = [site for site in sites if site["id_solar_edge"]]

    tasks = [
        solar_service.get_env_benefits(
            solar_edge_site["id_solar_edge"],
            solar_edge_site["custom_api_key"],
        )
        for solar_edge_site in solar_edge_sites
    ]
    results = await asyncio.gather(*tasks)

    total_co2_emission_saved = 0
    total_trees_planted = 0
    for result in results:
        total_co2_emission_saved += result["envBenefits"]["gasEmissionSaved"]["co2"]
        total_trees_planted += result["envBenefits"]["treesPlanted"]

    response = {
        "total_co2_emission_saved": round(total_co2_emission_saved, 2),
        "total_trees_planted": round(total_trees_planted, 2),
        "total_solar_sites": len(solar_edge_sites),
    }

    return response


@router.post("/solar_edge_sites")
async def upload_solar_edge_sites(uploaded_site: UploadedSolarEdgeSite = Body(...)):
    docs = (
        db.collection("uploaded_sites")
        .where(filter=FieldFilter("id_solar_edge", "==", uploaded_site.id_solar_edge))
        .stream()
    )

    sites = [{"id": doc.id, **doc.to_dict()} async for doc in docs]
    if len(sites):
        site = sites[0]
        await db.collection("uploaded_sites").document(site["id"]).set(
            dict(uploaded_site)
        )
        if not site["active"]:
            await db.collection("sites").document(site["id"]).delete()

    else:
        await db.collection("uploaded_sites").add(dict(uploaded_site))

    return "Successful upload!"
