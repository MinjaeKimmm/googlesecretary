from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import get_settings
from src.routes import auth, calendar, email, drive
from src.services.database.mongodb import init_db
from src.services.database.elastic import init_elastic
from src.services.database.elastic import return_drive

import os



app = FastAPI(title="Google Workspace Assistant API")
# get location of current folder
os.environ["ROOT_LOCATION"] = os.path.dirname(os.path.abspath(__file__))
# Load settings
settings = get_settings()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_client():
    await init_db()
    await init_elastic()

@app.get("/", tags=["root"])
def welcome():
    return {"message": "Welcome to Google Workspace Assistant API!"}

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])
app.include_router(email.router, prefix="/api/email", tags=["email"])
app.include_router(drive.router, prefix="/api/drive", tags=["drive"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=False)