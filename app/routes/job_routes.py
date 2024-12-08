import aiohttp
from fastapi import APIRouter, BackgroundTasks

from app.jobs.scheduled_jobs import (
    merge_sites,
    refresh_selenium_session_cookie,
    update_site_images,
)

router = APIRouter()


@router.post("/trigger_hourly_job")
async def trigger_hourly_job(background_tasks: BackgroundTasks):
    background_tasks.add_task(refresh_selenium_session_cookie)
    return {"message": "refresh_selenium_session_cookie sent in the background"}


@router.post("/trigger_2am_job")
async def trigger_2am_job(background_tasks: BackgroundTasks):
    background_tasks.add_task(merge_sites)
    return {"message": "merge_sites sent in the background"}


@router.post("/trigger_3am_job")
async def trigger_3am_job(background_tasks: BackgroundTasks):
    background_tasks.add_task(update_site_images)
    return {"message": "update_site_images sent in the background"}


async def trigger_fake_traffic():
    print("Start faking traffic every 14 minutes to prevent Render from sleeping...")
    url = "https://energy-dashboard-api-o69l.onrender.com/dummy_endpoint"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            await response.json()

    print("Finished faking traffic")
