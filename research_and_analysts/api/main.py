from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

import os
from research_and_analysts.api.routes import report_routes
from datetime import datetime

app = FastAPI(title="Autonomus Report Generation UI")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="research_and_analysts/api/templates")
app.templates = templates

def basename_filter(path:str):
    return os.path.basename(path)

templates.env.filters["basename"] = basename_filter

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return{
        "status":"healthy",
        "service":"research-report-generation",
        "timestamp":datetime.now().isoformat()
    }

app.include_router(report_routes.router)