from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import get_settings
from src.routes import auth, calendar #, email, drive
from src.services.database.mongodb import init_db

app = FastAPI(title="Google Workspace Assistant API")

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
async def startup_db_client():
    await init_db()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])
#app.include_router(email.router, prefix="/api/email", tags=["email"])
#app.include_router(drive.router, prefix="/api/drive", tags=["drive"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)