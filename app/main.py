from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routes import job_routes, site_routes

app = FastAPI()

app.include_router(site_routes.router)
app.include_router(job_routes.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    # Return the exact error message to the client
    return JSONResponse(status_code=500, content={"detail": str(exc)})
