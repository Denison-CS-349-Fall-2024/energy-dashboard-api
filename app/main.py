import pytz
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.jobs.scheduled_jobs import (
    merge_sites,
    refresh_selenium_session_cookie,
    update_site_images,
)
from app.routes import job_routes, site_routes

app = FastAPI()
EST = pytz.timezone("US/Eastern")
scheduler = AsyncIOScheduler(timezone=EST)

app.include_router(site_routes.router)
app.include_router(job_routes.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


scheduler.add_job(
    job_routes.trigger_fake_traffic, IntervalTrigger(minutes=14, timezone=EST)
)
scheduler.add_job(
    refresh_selenium_session_cookie, IntervalTrigger(hours=1, timezone=EST)
)
scheduler.add_job(
    merge_sites,
    CronTrigger(hour=2, minute=0, timezone=EST),
)
scheduler.add_job(
    update_site_images,
    CronTrigger(hour=3, minute=0, timezone=EST),
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.on_event("startup")
async def startup_event():
    scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000, reload=False)
