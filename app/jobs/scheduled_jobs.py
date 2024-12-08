import asyncio
import collections
from datetime import datetime, time

import pandas as pd
import pytz
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.config import settings
from app.db import db
from app.helpers.helpers import merge_sites_from_solar_edge_and_energy_star
from app.routes.site_routes import read_sites
from app.services.selenium_services import selenium_service
from app.services.solar_services import solar_service


async def refresh_selenium_session_cookie():
    est_tz = pytz.timezone("US/Eastern")
    current_time_est = datetime.now(est_tz)
    current_time = current_time_est.time()
    if time(3, 0) <= current_time < time(4, 0):
        print(
            f"Skipping task. It's between 3 AM and 4 AM EST Current time: {current_time_est.strftime('%H:%M:%S')}"
        )
        return

    print("Start running refresh_selenium_session_cookie...")
    data = {
        "cookie": selenium_service.get_session_cookie(),
        "created_at": firestore.SERVER_TIMESTAMP,
    }
    await db.collection("cookies").document("0TuYMeLMOe0Vqqp6UyiD").set(data)
    print("Finished running refresh_selenium_session_cookie")


async def merge_sites():
    print("Start running merge_sites...")
    # Source 1: enery star sites through Selenium
    energy_star_sites = selenium_service.get_energy_star_sites()
    # Source 2: solar sites through API
    solar_edge_sites = (await solar_service.get_all_sites(settings.API_KEY_SOLAR_EDGE))[
        "sites"
    ]["site"]
    # Source 3: solar sites through custom uploads. `uploaded_solar_edge_sites` are guaranteed to be distinct from `solar_edge_sites`
    docs = db.collection("uploaded_sites").stream()
    uploaded_solar_edge_sites = [{**doc.to_dict()} async for doc in docs]

    merged_df = merge_sites_from_solar_edge_and_energy_star(
        solar_edge_sites, energy_star_sites, uploaded_solar_edge_sites
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
        custom_api_key = (
            row["custom_api_key"] if pd.notna(row["custom_api_key"]) else None
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
            "custom_api_key": custom_api_key,
        }

        # Upsert the document into the "sites" collection
        await db.collection("sites").document(doc_id).set(doc_data)

    print("Finished running merge_sites")


async def update_site_images():
    print("Start running update_site_images...")
    api_key_table = collections.defaultdict(
        set
    )  # mapping {api_key: [id_solar_edge, ...]}
    id_solar_edge_table = {}  # mapping {id_solar_edge: api_key}
    energy_star_ids = set()

    sites = await read_sites()
    for site in sites:
        if site["id_solar_edge"]:
            api_key_table[site["custom_api_key"]].add(site["id_solar_edge"])
            id_solar_edge_table[site["id_solar_edge"]] = site["custom_api_key"]
        if site["id_energy_star"]:
            energy_star_ids.add(site["id_energy_star"])

    tasks = [
        solar_service.get_site_details(id_solar_edge, api_key)
        for api_key, id_solar_edge_list in api_key_table.items()
        for id_solar_edge in id_solar_edge_list
    ]
    results = await asyncio.gather(*tasks)

    # update images for solar edge
    for result in results:
        entry = result["details"]
        id_solar_edge = entry["id"]
        image_url = entry["uris"].get("SITE_IMAGE", None)
        site_api_key = id_solar_edge_table[id_solar_edge]
        if image_url:
            image_url = (
                f"https://monitoringapi.solaredge.com{image_url}?api_key={site_api_key}"
            )
            docs = (
                db.collection("sites")
                .where(filter=FieldFilter("id_solar_edge", "==", id_solar_edge))
                .stream()
            )
            doc_data = [{"id": doc.id, **doc.to_dict()} async for doc in docs][0]
            doc_data.update({"site_image_url": image_url})
            await db.collection("sites").document(doc_data["id"]).set(doc_data)

    # update images for energy star
    site_image_urls = selenium_service.get_energy_star_images(energy_star_ids)
    for id_energy_star, image_url in site_image_urls.items():
        docs = (
            db.collection("sites")
            .where(filter=FieldFilter("id_energy_star", "==", id_energy_star))
            .stream()
        )
        doc_data = [{"id": doc.id, **doc.to_dict()} async for doc in docs][0]
        doc_data.update({"site_image_url": image_url})
        await db.collection("sites").document(doc_data["id"]).set(doc_data)

    print("Finished running update_site_images")
