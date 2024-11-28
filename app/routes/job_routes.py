from fastapi import APIRouter, BackgroundTasks

from app.jobs.scheduled_jobs import (
    merge_sites,
    refresh_selenium_session_cookie,
    update_site_images,
)

router = APIRouter()


@router.post("/trigger_2am_job")
def trigger_2am_job(background_tasks: BackgroundTasks):
    background_tasks.add_task(merge_sites)
    print("2AM JOB ALERT: merge_sites sent in the background")
    return {"message": "merge_sites sent in the background"}


@router.post("/trigger_3am_job")
def trigger_3am_job(background_tasks: BackgroundTasks):
    background_tasks.add_task(update_site_images)
    print("3AM JOB ALERT: update_site_images sent in the background")
    return {"message": "update_site_images sent in the background"}


@router.post("/trigger_hourly_job")
def trigger_hourly_job(background_tasks: BackgroundTasks):
    background_tasks.add_task(refresh_selenium_session_cookie)
    print("HOURLY JOB ALERT: refresh_selenium_session_cookie sent in the background")
    return {"message": "refresh_selenium_session_cookie sent in the background"}
