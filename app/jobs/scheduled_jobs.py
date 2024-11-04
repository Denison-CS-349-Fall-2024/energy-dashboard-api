import pandas as pd
from firebase_admin import firestore

from app.helpers.helpers import merge_sites_from_solar_edge_and_energy_star
from app.services.selenium_services import selenium_service
from app.services.solar_services import solar_service

from ..db import db


async def merge_sites():
    solar_edge_sites = (await solar_service.get_all_sites())["sites"]["site"]
    # add dummy for testing
    solar_edge_sites.append({"id": 123, "name": "Loccc Ppham", "status": "Active"})
    solar_edge_sites.append({"id": 28521507, "name": "Pratt Hall", "status": "Active"})

    energy_star_sites = selenium_service.get_energy_star_sites()
    # add dummy for testing
    energy_star_sites.append(
        {
            "id": 285289311,
            "name": "Loc Pham",
        }
    )
    energy_star_sites.append(
        {
            "id": 1212087,
            "name": "Pratt Hall",
        }
    )
    merged_df = merge_sites_from_solar_edge_and_energy_star(
        solar_edge_sites, energy_star_sites
    )
    for index, row in merged_df.iterrows():
        id_solar_edge = (
            int(row["id_solar_edge"]) if pd.notna(row["id_solar_edge"]) else None
        )
        id_energy_star = (
            int(row["id_energy_star"]) if pd.notna(row["id_energy_star"]) else None
        )
        name_solar_edge = (
            row["name_solar_edge"] if pd.notna(row["name_solar_edge"]) else None
        )
        name_energy_star = (
            row["name_energy_star"] if pd.notna(row["name_energy_star"]) else None
        )
        internal_name = row["internal_name"]
        doc_id = f"{id_solar_edge}__{id_energy_star}"

        # Prepare the document data
        doc_data = {
            "name_solar_edge": name_solar_edge,
            "name_energy_star": name_energy_star,
            "internal_name": internal_name,
            "id_energy_star": id_energy_star,
            "id_solar_edge": id_solar_edge,
        }

        # Upsert the document into the "sites" collection
        await db.collection("sites").document(doc_id).set(doc_data)


async def refresh_selenium_session_cookie():
    data = {
        "cookie": selenium_service.get_session_cookie(),
        "created_at": firestore.SERVER_TIMESTAMP,
    }
    await db.collection("cookies").document("0TuYMeLMOe0Vqqp6UyiD").set(data)
