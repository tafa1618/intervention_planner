from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from database import get_db, AsyncSessionLocal
from services.ingestion import ingest_programmes_data
from routers import interventions, machines, auth, admin
from models import User
from routers.auth import get_password_hash
import os

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # Create admin user if not exists
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.email == "admin@neemba.com")
        )
        user = result.scalar_one_or_none()

        if not user:
            admin_user = User(
                email="admin@neemba.com",
                full_name="Admin",
                password_hash=get_password_hash("admin123"),
                role="admin",
                is_active=True,
            )
            db.add(admin_user)
            await db.commit()
            print("✅ Admin user created")
        else:
            print("ℹ️ Admin already exists")


# Routers
app.include_router(interventions.router)
app.include_router(machines.router)
app.include_router(auth.router)
app.include_router(admin.router)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Intervention Planner Backend Running"}


@app.get("/migrations/status")
async def get_migration_status(db: AsyncSession = Depends(get_db)):
    """Get current database migration status"""
    try:
        result = await db.execute(text("SELECT version_num FROM alembic_version"))
        current_version = result.scalar_one_or_none()
        
        return {
            "status": "ok",
            "current_revision": current_version,
            "message": "Database migrations applied successfully" if current_version else "No migrations applied yet"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "current_revision": None
        }


@app.post("/upload-programmes")
async def upload_machines_excel(
    file: UploadFile = File(...), db: AsyncSession = Depends(get_db)
):
    try:
        temp_file = f"/tmp/uploaded_{file.filename}"
        with open(temp_file, "wb") as f:
            f.write(await file.read())

        # Process the file
        stats = await ingest_programmes_data(temp_file, db)

        # Clean up
        os.remove(temp_file)

        await db.commit()
        return {"message": "File processed successfully", "stats": stats}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "ok"}
