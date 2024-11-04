from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.jobs.scheduled_jobs import merge_sites, refresh_selenium_session_cookie

from .routes import site_routes

app = FastAPI()

# app.include_router(auth_routes.router)
app.include_router(site_routes.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


@app.on_event("startup")
async def startup_event():
    # await merge_sites()
    # await refresh_selenium_session_cookie()
    pass


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    # Return the exact error message to the client
    return JSONResponse(status_code=500, content={"detail": str(exc)})
